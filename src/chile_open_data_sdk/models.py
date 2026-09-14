"""Public response models for CKAN Action API envelopes."""

from pydantic import BaseModel, ConfigDict, Field, JsonValue, StrictBool, StrictInt


class ActionResponse(BaseModel):
    """CKAN envelope with strict success typing and preserved extension metadata.

    This model validates structure only. Use parse_response to enforce result
    presence, map failures, and redact diagnostics; model contents remain raw."""

    model_config = ConfigDict(extra="allow")
    success: StrictBool
    result: JsonValue = None
    error: dict[str, JsonValue] | None = None


class CatalogModel(BaseModel):
    """Metadata with preserved plugin fields and no forced date/URL conversion."""

    model_config = ConfigDict(extra="allow")


class Tag(CatalogModel):
    """A free tag or vocabulary tag; identifiers remain upstream strings."""

    id: str
    name: str
    display_name: str | None = None
    vocabulary_id: str | None = None


class Group(CatalogModel):
    """Common group metadata shared by list, show, and dataset responses."""

    id: str
    name: str
    title: str | None = None
    description: str | None = None
    display_name: str | None = None
    image_display_url: str | None = None
    package_count: int | None = None
    state: str | None = None


class Organization(Group):
    """An organization that owns datasets."""

    is_organization: bool | None = None


class Resource(CatalogModel):
    """Resource metadata; URL and date strings are preserved, never fetched."""

    id: str
    url: str | None = None
    name: str | None = None
    description: str | None = None
    format: str | None = None
    mimetype: str | None = None
    package_id: str | None = None
    datastore_active: bool | None = None
    created: str | None = None
    last_modified: str | None = None
    size: int | float | str | None = None


class Dataset(CatalogModel):
    """Dataset (CKAN package) metadata with typed nested catalog entities."""

    id: str
    name: str
    title: str | None = None
    notes: str | None = None
    url: str | None = None
    state: str | None = None
    private: bool | None = None
    license_id: str | None = None
    license_title: str | None = None
    owner_org: str | None = None
    organization: Organization | None = None
    resources: list[Resource] = Field(default_factory=list)
    groups: list[Group] = Field(default_factory=list)
    tags: list[Tag] = Field(default_factory=list)
    metadata_created: str | None = None
    metadata_modified: str | None = None


class DatasetSearchResult(CatalogModel):
    """One search page, total matching count, and preserved facet metadata."""

    count: StrictInt = Field(ge=0)
    results: list[Dataset]
    facets: dict[str, JsonValue] = Field(default_factory=dict)
    search_facets: dict[str, JsonValue] = Field(default_factory=dict)
