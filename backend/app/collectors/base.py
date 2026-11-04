"""Base Protocol & Data Models for Data Source Adapters.

Defines the contract that Adapter A, Adapter B, and Adapter C must satisfy.
"""

from typing import Protocol, TypeVar, Generic, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class Money(BaseModel):
    amount: float = Field(default=0.0, ge=0.0)
    currency: str = Field(default="USD")


class Capabilities(BaseModel):
    commercial_ads: bool = Field(description="Can retrieve commercial product and service ads")
    political_ads: bool = Field(description="Can retrieve political and social issue ads")
    spend_ranges: bool = Field(description="Exposes spend and impression lower/upper bounds")
    page_based_query: bool = Field(description="Supports querying all ads by specific Meta page_id")
    keyword_query: bool = Field(description="Supports full-text keyword searches across ad body text")
    only_new_ads: bool = Field(description="Supports delta fetching since last crawl timestamp")
    max_page_size: int = Field(default=100, ge=1, le=500)


class SearchQuery(BaseModel):
    city_slug: str
    country_code: str = "IN"
    keyword: str | None = None
    page_id: str | None = None
    languages: list[str] = Field(default_factory=list)
    limit: int = 50
    active_only: bool = True
    since_date: datetime | None = None


class RawAd(BaseModel):
    meta_ad_id: str
    meta_page_id: str
    page_name: str
    source_adapter: str
    ad_type: str = "commercial"  # commercial | political_issue
    delivery_start: datetime | None = None
    delivery_stop: datetime | None = None
    body_text: str | None = None
    headline: str | None = None
    cta: str | None = None
    landing_url: str | None = None
    landing_domain: str | None = None
    media_type: str | None = None
    platforms: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    collation_id: str | None = None
    collation_count: int = 1
    # Political transparency fields
    spend_lower: int | None = None
    spend_upper: int | None = None
    impressions_lower: int | None = None
    impressions_upper: int | None = None
    currency: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)


T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    total_estimated: int | None = None


class AdapterHealth(BaseModel):
    adapter_name: str
    is_healthy: bool
    status_message: str
    last_checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdSourceAdapter(Protocol):
    name: str
    schema_version: int

    def capabilities(self) -> Capabilities:
        ...

    def estimate_cost(self, q: SearchQuery) -> Money:
        ...

    async def search(self, q: SearchQuery, cursor: str | None = None) -> Page[RawAd]:
        ...

    async def by_page(self, page_id: str, cursor: str | None = None, active_only: bool = True) -> Page[RawAd]:
        ...

    async def health(self) -> AdapterHealth:
        ...

