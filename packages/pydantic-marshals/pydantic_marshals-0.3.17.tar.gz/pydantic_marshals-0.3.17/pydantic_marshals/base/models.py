from collections.abc import Iterator
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, create_model

from pydantic_marshals.base.fields.base import MarshalField
from pydantic_marshals.base.type_aliases import FieldType


class MarshalBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FieldConverter:
    field_types: tuple[type[MarshalField], ...] = ()
    """Field types to be used in :py:meth:`convert_field`"""

    @classmethod
    def dynamic_field_types(cls) -> Iterator[type[MarshalField]]:
        """
        Same as :py:attr:`field_types`, but these could be dynamically generated.
        Generated values would be added to the end of `field_types`
        """
        yield from ()  # noqa: WPS353

    default_field_type: type[MarshalField] | None = None
    """Last field type to try if others don't work"""

    @classmethod
    def collect_field_types(cls) -> Iterator[type[MarshalField]]:
        yield from cls.field_types
        yield from cls.dynamic_field_types()
        if cls.default_field_type is not None:
            yield cls.default_field_type

    def __init_subclass__(cls, **_: Any) -> None:
        cls.field_types = tuple(cls.collect_field_types())

    @classmethod
    def convert_field(cls, raw_field: Any) -> MarshalField:
        """
        Converts "raw_field"s into :py:class:`MarshalField` by trying to call
        the .convert method on all of :py:attr:`field_types` in this class.
        Will raise a `RuntimeError` if none of them return MarshalField
        """
        if isinstance(raw_field, MarshalField):
            return raw_field

        if not isinstance(raw_field, tuple):
            raw_field = (raw_field,)

        for field_type in cls.field_types:
            field: MarshalField | None = field_type.convert(*raw_field)
            if field is not None:
                return field
        raise RuntimeError(f"Couldn't convert field: {raw_field}")

    @classmethod
    def convert_aliased_field(cls, raw_field: Any, alias: str | None) -> MarshalField:
        """
        Same as :py:meth:`.convert_field`, but also adds an ``alias`` to the field
        """
        field = cls.convert_field(raw_field)
        field.alias = alias
        return field

    @classmethod
    def convert_fields(
        cls,
        *fields: Any,
        **aliased_fields: Any,
    ) -> Iterator[MarshalField]:
        """
        Converts all arguments into :py:class:`MarshalField`s
        via :py:meth:`.convert_field` and :py:meth:`.convert_aliased_field`

        :param fields: un-aliased positional arguments for fields, can be tuples
        :param aliased_fields: same as fields, but keys are used as aliases
        :return: yields resulting MappedFields one by one
        :raises RuntimeError: if conversion of one of the fields fails
        """
        yield from (cls.convert_field(field) for field in fields)
        yield from (
            cls.convert_aliased_field(field, alias)
            for alias, field in aliased_fields.items()
        )


class MarshalModel(FieldConverter):
    """
    Basic boilerplate class for all pydantic-marshals models.
    This is a complete class, but it could be extended with alternative constructors,
    updated base model, new runtime methods or auto-converters for fields
    """

    def __init__(
        self,
        *fields: MarshalField,
        bases: list[type[BaseModel]],
        extra_fields: dict[str, FieldType],
    ) -> None:
        """
        :param fields: fields to include in the model
        :param bases: pydantic bases to add to the model
        """
        self.fields: list[MarshalField] = list(fields)
        self.bases: list[type[BaseModel]] = bases
        self.extra_fields: dict[str, FieldType] = extra_fields
        self._generated_model: type[BaseModel] | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.model_name: str = f"{owner.__qualname__}.{name}"

    model_base_class: ClassVar[type[BaseModel]] = MarshalBaseModel
    """Base model class. Subclasses of :py:class:`MarshalBaseModel` are recommended"""

    def generate_base(self) -> type[BaseModel] | tuple[type[BaseModel], ...]:
        """Generate __base__ argument for :py:func:`create_model`"""
        if len(self.bases) == 0:
            return self.model_base_class
        return tuple(self.bases)

    def generate_model(self) -> type[BaseModel]:
        """Generate the pydantic model"""
        return create_model(  # type: ignore[call-overload, no-any-return]
            self.model_name,
            __base__=self.generate_base(),
            **{
                mapped_field.generate_name(): mapped_field.generate_field()
                for mapped_field in self.fields
            },
            **self.extra_fields,
        )

    @property
    def generated_model(self) -> type[BaseModel]:
        """
        Pydantic model, generated by the MarshalModel
        First call to this will call :py:meth:`.generate_model`,
        then save the result to :py:attr:`._generated_model`,
        for it to be reused on future calls
        """
        if self._generated_model is None:
            self._generated_model = self.generate_model()
        return self._generated_model

    def __get__(
        self,
        instance: Any,  # noqa: U100
        owner: Any | None = None,  # noqa: U100
    ) -> type[BaseModel]:
        return self.generated_model
