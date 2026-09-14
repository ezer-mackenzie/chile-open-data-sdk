"""Typed synchronous catalog services sharing the client's generic action transport."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING

from pydantic import TypeAdapter

from chile_open_data_sdk.constants import (
    DEFAULT_CATALOG_LIMIT,
    DEFAULT_DATASET_SORT,
    DEFAULT_PAGE_SIZE,
    DEFAULT_SEARCH_ROWS,
)
from chile_open_data_sdk.errors import CKANProtocolError
from chile_open_data_sdk.models import (
    Dataset,
    DatasetSearchResult,
    Group,
    Organization,
    Resource,
    Tag,
)
from chile_open_data_sdk.responses import parse_result
from chile_open_data_sdk.types import JSONObject, JSONValue
from chile_open_data_sdk.validation import validate_identifier, validate_page_value

if TYPE_CHECKING:
    from chile_open_data_sdk.client import ActionService


class DatasetService:
    """Discover dataset names, search metadata, and explicitly iterate pages."""

    def __init__(self, actions: ActionService) -> None:
        self.actions = actions

    def list(self, *, limit: int = DEFAULT_PAGE_SIZE, offset: int = 0) -> list[str]:
        """Return one page of dataset names using package_list."""
        validate_page_value(limit, "limit", minimum=1)
        validate_page_value(offset, "offset")
        result = self.actions.call("package_list", {"limit": limit, "offset": offset})
        return parse_result(result, TypeAdapter(list[str]), "package_list")

    def get(self, id: str) -> Dataset:
        """Look up one dataset by upstream ID or name."""
        validate_identifier(id)
        result = self.actions.call("package_show", {"id": id})
        return parse_result(result, TypeAdapter(Dataset), "package_show")

    def search(
        self,
        q: str = "*:*",
        *,
        fq: str | None = None,
        sort: str | None = None,
        rows: int = DEFAULT_SEARCH_ROWS,
        start: int = 0,
        extra_params: Mapping[str, JSONValue] | None = None,
    ) -> DatasetSearchResult:
        """Return one package_search page; rows=0 supports count/facet-only queries.

        Queries are passed through unchanged. extra_params supports plugin and
        dotted facet parameters, but cannot override q, fq, sort, rows, or start.
        """
        validate_page_value(rows, "rows")
        validate_page_value(start, "start")
        params: JSONObject = dict(extra_params) if extra_params is not None else {}
        if params.keys() & {"q", "fq", "sort", "rows", "start"}:
            raise ValueError("extra_params cannot override named search parameters")
        params.update({"q": q, "rows": rows, "start": start})
        if fq is not None:
            params["fq"] = fq
        if sort is not None:
            params["sort"] = sort
        result = self.actions.call("package_search", params)
        return parse_result(result, TypeAdapter(DatasetSearchResult), "package_search")

    def iter_pages(
        self,
        q: str = "*:*",
        *,
        fq: str | None = None,
        sort: str = DEFAULT_DATASET_SORT,
        page_size: int = DEFAULT_PAGE_SIZE,
        start: int = 0,
        extra_params: Mapping[str, JSONValue] | None = None,
    ) -> Iterator[DatasetSearchResult]:
        """Lazily fetch pages, advancing by actual returned size, with a stable sort.

        Stop on an empty page or at the first page's total count. A consecutive
        repeated page raises CKANProtocolError. Offset paging is not a snapshot:
        concurrent catalog edits can still cause omissions or duplicates.
        """
        validate_page_value(page_size, "page_size", minimum=1)
        validate_page_value(start, "start")
        stop: int | None = None
        previous: tuple[str, ...] | None = None
        while stop is None or start < stop:
            page = self.search(
                q, fq=fq, sort=sort, rows=page_size, start=start, extra_params=extra_params
            )
            if not page.results:
                return
            signature = tuple(dataset.id for dataset in page.results)
            if signature == previous:
                raise CKANProtocolError(
                    "Catalog pagination did not advance", action="package_search"
                )
            previous = signature
            if stop is None:
                stop = page.count
            start += len(page.results)
            yield page

    def iter_search(
        self,
        q: str = "*:*",
        *,
        fq: str | None = None,
        sort: str = DEFAULT_DATASET_SORT,
        page_size: int = DEFAULT_PAGE_SIZE,
        start: int = 0,
        max_items: int | None = None,
        extra_params: Mapping[str, JSONValue] | None = None,
    ) -> Iterator[Dataset]:
        """Lazily yield datasets, optionally bounded by max_items (zero makes no request).

        At most one page is buffered. The last fetched page may contain more items
        than yielded when max_items falls within it. Validation runs on iteration.
        """
        validate_page_value(page_size, "page_size", minimum=1)
        validate_page_value(start, "start")
        if max_items is not None:
            validate_page_value(max_items, "max_items")
            if max_items == 0:
                return
        emitted = 0
        for page in self.iter_pages(
            q, fq=fq, sort=sort, page_size=page_size, start=start, extra_params=extra_params
        ):
            for dataset in page.results:
                yield dataset
                emitted += 1
                if max_items is not None and emitted >= max_items:
                    return


class ResourceService:
    """Retrieve resource metadata without downloading its URL."""

    def __init__(self, actions: ActionService) -> None:
        self.actions = actions

    def get(self, id: str) -> Resource:
        """Look up a resource by its upstream string ID."""
        validate_identifier(id)
        result = self.actions.call("resource_show", {"id": id})
        return parse_result(result, TypeAdapter(Resource), "resource_show")


class OrganizationService:
    """Discover organizations with explicit, single-page metadata requests."""

    def __init__(self, actions: ActionService) -> None:
        self.actions = actions

    def list(
        self, *, limit: int = DEFAULT_CATALOG_LIMIT, offset: int = 0, sort: str = "name asc"
    ) -> list[Organization]:
        """Return one organization_list page with all_fields enabled."""
        validate_page_value(limit, "limit", minimum=1)
        validate_page_value(offset, "offset")
        result = self.actions.call(
            "organization_list",
            {
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "all_fields": True,
            },
        )
        return parse_result(result, TypeAdapter(list[Organization]), "organization_list")

    def get(self, id: str) -> Organization:
        """Look up an organization by ID or name, without embedded datasets/users."""
        validate_identifier(id)
        result = self.actions.call(
            "organization_show",
            {
                "id": id,
                "include_datasets": False,
                "include_users": False,
            },
        )
        return parse_result(result, TypeAdapter(Organization), "organization_show")


class GroupService:
    """Discover groups with explicit, single-page metadata requests."""

    def __init__(self, actions: ActionService) -> None:
        self.actions = actions

    def list(
        self, *, limit: int = DEFAULT_CATALOG_LIMIT, offset: int = 0, sort: str = "name asc"
    ) -> list[Group]:
        """Return one group_list page with all_fields enabled."""
        validate_page_value(limit, "limit", minimum=1)
        validate_page_value(offset, "offset")
        result = self.actions.call(
            "group_list",
            {
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "all_fields": True,
            },
        )
        return parse_result(result, TypeAdapter(list[Group]), "group_list")

    def get(self, id: str) -> Group:
        """Look up a group by ID or name, without embedded datasets/users."""
        validate_identifier(id)
        result = self.actions.call(
            "group_show",
            {
                "id": id,
                "include_datasets": False,
                "include_users": False,
            },
        )
        return parse_result(result, TypeAdapter(Group), "group_show")


class TagService:
    """Discover free tags or tags in an explicitly selected vocabulary."""

    def __init__(self, actions: ActionService) -> None:
        self.actions = actions

    def list(self, *, query: str | None = None, vocabulary_id: str | None = None) -> list[Tag]:
        """Return matching tag metadata; CKAN tag_list has no limit/offset contract."""
        params: JSONObject = {"all_fields": True}
        if query is not None:
            params["query"] = query
        if vocabulary_id is not None:
            params["vocabulary_id"] = vocabulary_id
        result = self.actions.call("tag_list", params)
        return parse_result(result, TypeAdapter(list[Tag]), "tag_list")

    def get(self, id: str, *, vocabulary_id: str | None = None) -> Tag:
        """Look up a tag by ID or name, without embedded datasets."""
        validate_identifier(id)
        params: JSONObject = {"id": id, "include_datasets": False}
        if vocabulary_id is not None:
            params["vocabulary_id"] = vocabulary_id
        result = self.actions.call("tag_show", params)
        return parse_result(result, TypeAdapter(Tag), "tag_show")
