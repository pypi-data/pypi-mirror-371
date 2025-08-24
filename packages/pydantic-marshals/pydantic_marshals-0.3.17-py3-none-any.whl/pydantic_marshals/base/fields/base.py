from __future__ import annotations

from collections.abc import Iterator
from enum import Enum
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import ConfigDict, RootModel
from pydantic.fields import Field
from pydantic_core import PydanticUndefined, PydanticUndefinedType
from typing_extensions import Self

from pydantic_marshals.base.type_aliases import FieldType, TypeHint

T = TypeVar("T")


class MarshalRootModel(RootModel[T], Generic[T]):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class MarshalField:
    """
    Basic boilerplate class for all pydantic-marshals' models' fields.
    This is an interface, and it requires implementing all methods to function
    and to be used in :py:class:`pydantic_marshals.models.base.MarshalModel`
    """

    marshal_root_model: ClassVar[type[RootModel[Any]]] = MarshalRootModel
    """Base root model class. Subclasses of :py:class:`MarshalRootModel` are recommended"""

    def __init__(self, alias: str | None = None) -> None:
        """
        :param alias: same as Field(alias=...), can be None for no alias
        """
        self.alias = alias

    @classmethod
    def convert(cls, *source: Any) -> Self | None:
        """
        Convert something into a field.
        If conversion is not possible, this method should return None
        """
        raise NotImplementedError

    def generate_name(self) -> str:
        """
        Generates the name for the field, used in
        :py:meth:`pydantic_marshals.models.base.MarshalModel.generate_model`
        """
        raise NotImplementedError

    def generate_type(self) -> TypeHint:
        """
        Generates the type annotation for the field, used in
        :py:meth:`pydantic_marshals.models.base.MarshalModel.generate_model`
        """
        raise NotImplementedError

    # TODO type with TypedDict? Use _FieldInfoInputs?
    def generate_field_data(self) -> Iterator[tuple[str, Any]]:
        """
        Generates field data (kwargs for :py:func:`pydantic.fields.Field`),
        and returns it in the for of an Iterator,
        compatible with the ``dict[str, Any]`` constructor

        Kwarg names and types can be found in
        :py:class:`pydantic.fields._FieldInfoInputs`
        """
        if self.alias is not None:
            yield "alias", self.alias

    def generate_field(self) -> FieldType:
        """
        Generates field info for the field, used in
        :py:meth:`pydantic_marshals.models.base.MarshalModel.generate_model`
        """
        return (
            self.generate_type(),
            Field(**dict(self.generate_field_data())),
        )

    def generate_root_model(self) -> type[RootModel[Any]]:
        # TODO maybe move to `contains`
        return self.marshal_root_model[self.generate_type()]  # type: ignore[no-any-return, index]


class PatchDefaultType(Enum):
    PatchDefault = object()


PatchDefault = PatchDefaultType.PatchDefault


class PatchMarshalField(MarshalField):
    def __init__(self, alias: str | None = None, patch: bool = False) -> None:
        """
        :param alias: same as Field(alias=...), can be None for no alias
        :param patch: use PatchDefault as a default for the filed
        """
        super().__init__(alias=alias)
        self.patch = patch

    def as_patch(self) -> Self:
        """
        Creates the same field (copy), but with patch=True
        """
        raise NotImplementedError

    def generate_default(self) -> Any | None | PydanticUndefinedType:
        """
        Generates the default for the field, used in
        :py:meth:`pydantic_marshals.models.base.MarshalModel.generate_field_data`
        """
        return PydanticUndefined

    def generate_field_data(self) -> Iterator[tuple[str, Any]]:
        yield "default", PatchDefault if self.patch else self.generate_default()

        yield from super().generate_field_data()
