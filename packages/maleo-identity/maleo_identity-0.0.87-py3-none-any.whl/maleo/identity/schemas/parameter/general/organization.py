from typing import List, Literal, Optional, overload
from uuid import UUID
from maleo.soma.constants import ALL_STATUSES
from maleo.soma.mixins.general import OptionalParentId
from maleo.soma.mixins.parameter import (
    IdentifierType as IdentifierTypeMixin,
    IdentifierValue as IdentifierValueMixin,
)
from maleo.soma.schemas.parameter.general import (
    ReadSingleQueryParameterSchema,
    ReadSingleParameterSchema,
)
from maleo.soma.types.base import ListOfDataStatuses
from maleo.metadata.schemas.data.organization_type import SimpleOrganizationTypeMixin
from maleo.identity.enums.organization import IdentifierType, ExpandableField
from maleo.identity.mixins.organization import Key, Name, Expand
from maleo.identity.types.base.organization import IdentifierValueType


class ReadSingleQueryParameter(Expand, ReadSingleQueryParameterSchema):
    pass


class ReadSingleParameter(
    Expand, ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.ID],
        value: int,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        expand: Optional[List[ExpandableField]] = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.UUID],
        value: UUID,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        expand: Optional[List[ExpandableField]] = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier: Literal[IdentifierType.KEY],
        value: str,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        expand: Optional[List[ExpandableField]] = None,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier: IdentifierType,
        value: IdentifierValueType,
        statuses: ListOfDataStatuses = ALL_STATUSES,
        use_cache: bool = True,
        expand: Optional[List[ExpandableField]] = None,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            value=value,
            statuses=statuses,
            use_cache=use_cache,
            expand=expand,
        )


class CreateOrUpdateBody(Name, Key, OptionalParentId, SimpleOrganizationTypeMixin):
    pass


class CreateParameter(
    Expand,
    CreateOrUpdateBody,
):
    pass


class UpdateParameter(
    Expand,
    CreateOrUpdateBody,
    IdentifierValueMixin[IdentifierValueType],
    IdentifierTypeMixin[IdentifierType],
):
    pass
