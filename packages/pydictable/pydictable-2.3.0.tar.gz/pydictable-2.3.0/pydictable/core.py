import inspect
from datetime import datetime
from enum import Enum
from typing import Dict, get_type_hints, Union, Type, Any

from pydictable.field import StrField, IntField, FloatField, BoolField, ListField, UnionField, NoneField, \
    ObjectField, DataValidationError, EnumField, DatetimeField, DictField, AnyField
from pydictable.type import _BaseDictAble, Field


class InvalidSchema(Exception):
    pass


TYPE_TO_FIELD = {
    str: StrField,
    int: IntField,
    float: FloatField,
    bool: BoolField,
    dict: DictField,
    type(None): NoneField,
    list: ListField,
    datetime: DatetimeField,
    Any: AnyField
}


class DictAble(_BaseDictAble):
    def __init__(self, *args, **kwargs):
        super(DictAble, self).__init__(*args, **kwargs)
        self.__clear_default_field_values()
        fields = self.get_fields()
        for k, v in kwargs.items():
            if k in fields:
                self.__setattr__(k, v)
        if kwargs.get('dict'):
            self.validate_dict(kwargs['dict'])
            self.__apply_dict(kwargs['dict'])
        if len(args) > 0:
            raise ReferenceError('Use kwargs to init DictAble')
        self.__set_defaults()
        self.__validate()
        try:
            self.validate()
        except AssertionError as e:
            raise DataValidationError('.', f'Validation failed with error: {str(e)}')

    @classmethod
    def __get_field_type_by_type_hint(cls, type_hint) -> Type[Field]:
        if type_hint in TYPE_TO_FIELD:
            return TYPE_TO_FIELD[type_hint]

        if '__origin__' in type_hint.__dict__ and type_hint.__origin__ == Union:
            return UnionField

        if '__origin__' in type_hint.__dict__ and type_hint.__origin__ == list:
            return ListField

        if '__origin__' in type_hint.__dict__ and type_hint.__origin__ == dict:
            return DictField

        if issubclass(type_hint, _BaseDictAble):
            return ObjectField
        if issubclass(type_hint, Enum):
            return EnumField
        raise NotImplementedError(f'Unsupported type hint {type_hint}')

    @classmethod
    def __get_field_by_type_hint(cls, type_hint):
        field_type = cls.__get_field_type_by_type_hint(type_hint)

        if field_type == UnionField:
            sub_types = []
            for sub_type in type_hint.__args__:
                sub_types.append(cls.__get_field_by_type_hint(sub_type))
            return UnionField(sub_types, required=True)

        if field_type == ListField:
            of_type = AnyField(required=True)
            if '__args__' in type_hint.__dict__:
                of_type = cls.__get_field_by_type_hint(type_hint.__args__[0])
            return ListField(of_type, required=True)

        if field_type == EnumField:
            return EnumField(type_hint, required=True, is_name=True)

        if field_type == ObjectField:
            return ObjectField(type_hint, required=True)

        if field_type == DictField:
            key_type, value_type = AnyField(required=True), AnyField(required=True)
            if '__args__' in type_hint.__dict__:
                key_type = cls.__get_field_by_type_hint(type_hint.__args__[0])
                value_type = cls.__get_field_by_type_hint(type_hint.__args__[1])

            return DictField(
                key_type=key_type,
                value_type=value_type,
                required=True
            )

        return field_type(required=True)

    @classmethod
    def get_fields(cls) -> Dict[str, Field]:
        fields = {}
        for attr in inspect.getmembers(cls):
            if isinstance(attr[1], Field):
                fields[attr[0]] = attr[1]
        for name, th in get_type_hints(cls).items():
            if name not in fields:
                fields[name] = cls.__get_field_by_type_hint(th)

        ordered_fields = {}
        for name in dict(vars(cls)).keys():
            if name in fields:
                ordered_fields[name] = fields[name]
        for k, v in fields.items():
            if k not in ordered_fields:
                ordered_fields[k] = v

        assert set(fields.keys()) == set(ordered_fields.keys())
        return ordered_fields

    @classmethod
    def get_field_key(cls, obj_attr: str):
        field = cls.get_fields()[obj_attr]
        return field.key if field.key else obj_attr

    def __clear_default_field_values(self):
        for attr, field in self.__class__.get_fields().items():
            self.__setattr__(attr, None)

    def __apply_dict(self, d: dict):
        for attr, field in self.__class__.get_fields().items():
            value = d.get(self.get_field_key(attr))
            if not field.required and value is None:
                continue
            self.__setattr__(attr, field.from_dict(value))

    @classmethod
    def validate_dict(cls, raw_values: dict):
        for attr, field in cls.get_fields().items():
            value = raw_values.get(cls.get_field_key(attr), field.default)
            if value is None and not field.required:
                continue
            try:
                field.validate_dict(attr, value)
            except DataValidationError as e:
                raise DataValidationError(f'{attr}.{e.path}', e.err)
            except AssertionError as e:
                if len(e.args) > 0:
                    raise DataValidationError(attr, f'Pre check failed: {str(e)}')
                raise DataValidationError(attr, f'Pre check failed: Invalid value {value} for field {attr}')

    def __validate(self):
        for attr, field in self.get_fields().items():
            value = self.__getattribute__(attr)
            if value is None and not field.required:
                continue
            try:
                field.validate(attr, value)
            except DataValidationError as e:
                raise DataValidationError(f'{attr}.{e.path}', e.err)
            except AssertionError:
                raise DataValidationError(attr,
                                          'Post check failed. Invalid value "{}" for field "{}"'.format(value, attr))

    def __set_defaults(self):
        for attr, field in self.get_fields().items():
            if field.required and field.default is not None:
                raise InvalidSchema(f'Both required and default passed for field {attr}')
            value = self.__getattribute__(attr)
            if value is None:
                if field.default is not None:
                    self.__setattr__(attr, field.default)
                elif field.default_factory:
                    func, args, kwargs = field.default_factory
                    self.__setattr__(attr, func(*args, **kwargs))

    def to_dict(self, skip_optional: bool = False) -> dict:
        d = {}
        for attr, field in self.__class__.get_fields().items():
            raw_value = self.__getattribute__(attr)
            if not field.required and raw_value is None:
                if skip_optional is False:
                    d[self.get_field_key(attr)] = None
                continue
            d[self.get_field_key(attr)] = field.to_dict(raw_value, skip_optional=skip_optional)
        return d

    @classmethod
    def get_input_spec(cls) -> dict:
        d = {}
        for attr, field in cls.get_fields().items():
            d[cls.get_field_key(attr)] = field.spec()
        return d

    def validate(self):
        pass


def partial(base_dictable: Type[DictAble]) -> Type[DictAble]:
    partial_attributes = {}
    for field_name, field_obj in base_dictable.get_fields().items():
        field_obj.required = False
        partial_attributes[field_name] = field_obj
    return type(f'Partial{base_dictable.__name__}', (base_dictable,), partial_attributes)
