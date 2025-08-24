from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, Relationship
from typing_extensions import Self

from pydantic_marshals.base.fields.base import PatchMarshalField
from pydantic_marshals.base.type_aliases import TypeHint
from pydantic_marshals.utils import ModeledType, is_subtype


class RelationshipField(PatchMarshalField):
    """
    Implementation of :py:class:`MarshalField` to use with SQLAlchemy's relationships
    A conversion model has to be specified, preferably one made with
    :py:class:`pydantic_marshals.models.sqlalchemy.MappedModel`
    """

    def __init__(
        self,
        mapped_relationship: Relationship[Any],
        model: type[BaseModel],
        nullable: bool = False,
        alias: str | None = None,
        patch: bool = False,
    ) -> None:
        super().__init__(alias, patch)
        self.relationship = mapped_relationship
        self.model = model
        self.nullable = nullable

    def as_patch(self) -> RelationshipField:
        return RelationshipField(
            mapped_relationship=self.relationship,
            model=self.model,
            nullable=self.nullable,
            alias=self.alias,
            patch=True,
        )

    @classmethod
    def convert(
        cls,
        mapped: Any = None,
        model: Any = None,
        nullable: Any = False,
        *_: Any,
    ) -> Self | None:
        if (
            isinstance(mapped, Relationship)
            and is_subtype(model, BaseModel)
            and isinstance(nullable, bool)
        ):
            return cls(mapped, model, nullable)
        return None

    def generate_name(self) -> str:
        return self.relationship.key

    def generate_type(self) -> TypeHint:
        collection_class = self.relationship.collection_class
        if collection_class is None:
            if self.nullable:
                return self.model | None
            return self.model
        if not isinstance(collection_class, type):
            raise RuntimeError(f"Collection is not a type: {collection_class}")
        if issubclass(collection_class, list):
            return list[self.model]  # type: ignore[name-defined]
        raise RuntimeError(f"Bad collection class: {collection_class}")


RelationshipType = (
    ModeledType[Relationship[Any]] | ModeledType[Mapped[Any]] | RelationshipField
)
