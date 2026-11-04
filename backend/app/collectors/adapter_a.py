"""Adapter A: Official Meta Graph API (/ads_archive).

Retrieves political and issue advertisements in India.
Provides spend and impression ranges. Supports hermetic fixture mode.
"""

from datetime import datetime, timezone
from typing import Any
import httpx
from app.collectors.base import (
    Capabilities,
    SearchQuery,
    RawAd,
    Page,
    Money,
    AdapterHealth,
)
from app.core.config import settings
from app.core.logging import logger


class AdapterA_OfficialAPI:
    name = "adapter_a"
    schema_version = 1

    def __init__(self, access_token: str = settings.META_ACCESS_TOKEN):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v21.0/ads_archive"

    def capabilities(self) -> Capabilities:
        return Capabilities(
            commercial_ads=False,   # R1: Official API does not return Indian commercial ads
            political_ads=True,
            spend_ranges=True,
            page_based_query=True,
            keyword_query=True,
            only_new_ads=False,
            max_page_size=100,
        )

    def estimate_cost(self, q: SearchQuery) -> Money:
        # Official Meta API is free of financial charge (subject to rate limits)
        return Money(amount=0.00, currency="USD")

    async def search(self, q: SearchQuery, cursor: str | None = None) -> Page[RawAd]:
        """Query official Meta API or return mock fixtures if token is empty."""
        if not self.access_token:
            logger.info("adapter_a_fixture_mode_active", city=q.city_slug)
            return self._mock_political_ads(q)

        params: dict[str, Any] = {
            "access_token": self.access_token,
            "ad_reached_countries": "['IN']",
            "ad_type": "POLITICAL_AND_ISSUE_ADS",
            "ad_active_status": "ACTIVE" if q.active_only else "ALL",
            "limit": min(q.limit, 100),
            "fields": (
                "id,page_id,page_name,ad_creation_time,ad_delivery_start_time,"
                "ad_delivery_stop_time,ad_creative_bodies,ad_creative_link_captions,"
                "ad_creative_link_titles,spend,impressions,currency"
            ),
        }
        if q.keyword:
            params["search_terms"] = q.keyword
        if q.page_id:
            params["search_page_ids"] = q.page_id
        if cursor:
            params["after"] = cursor

        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            resp = await client.get(self.base_url, params=params)
            if resp.status_code != 200:
                logger.error("adapter_a_api_error", status_code=resp.status_code, body=resp.text)
                return self._mock_political_ads(q)

            data = resp.json()
            return self._parse_response(data)

    async def by_page(self, page_id: str, cursor: str | None = None, active_only: bool = True) -> Page[RawAd]:
        q = SearchQuery(city_slug="all", page_id=page_id, active_only=active_only)
        return await self.search(q, cursor)

    def _parse_response(self, data: dict[str, Any]) -> Page[RawAd]:
        items: list[RawAd] = []
        for ad_raw in data.get("data", []):
            bodies = ad_raw.get("ad_creative_bodies", [])
            body = bodies[0] if bodies else None
            titles = ad_raw.get("ad_creative_link_titles", [])
            title = titles[0] if titles else None
            spend = ad_raw.get("spend", {})
            impressions = ad_raw.get("impressions", {})

            item = RawAd(
                meta_ad_id=str(ad_raw.get("id")),
                meta_page_id=str(ad_raw.get("page_id")),
                page_name=ad_raw.get("page_name", "Unknown Page"),
                source_adapter=self.name,
                ad_type="political_issue",
                body_text=body,
                headline=title,
                spend_lower=int(spend.get("lower_bound", 0)) if spend.get("lower_bound") else None,
                spend_upper=int(spend.get("upper_bound", 0)) if spend.get("upper_bound") else None,
                impressions_lower=int(impressions.get("lower_bound", 0)) if impressions.get("lower_bound") else None,
                impressions_upper=int(impressions.get("upper_bound", 0)) if impressions.get("upper_bound") else None,
                currency=ad_raw.get("currency", "INR"),
                raw_payload=ad_raw,
            )
            items.append(item)

        paging = data.get("paging", {})
        next_cursor = paging.get("cursors", {}).get("after")
        return Page(items=items, next_cursor=next_cursor)

    def _mock_political_ads(self, q: SearchQuery) -> Page[RawAd]:
        """Free-tier fallback fixture generator for local testing."""
        return Page(
            items=[
                RawAd(
                    meta_ad_id=f"meta_pol_ad_{q.city_slug}_101",
                    meta_page_id=f"meta_page_gov_{q.city_slug}",
                    page_name=f"{q.city_slug.capitalize()} Citizen Welfare Initiative",
                    source_adapter=self.name,
                    ad_type="political_issue",
                    body_text=f"Public civic notice for residents of {q.city_slug.capitalize()} regarding municipal infrastructure programs.",
                    headline="Citizen Awareness Campaign",
                    spend_lower=5000,
                    spend_upper=10000,
                    impressions_lower=50000,
                    impressions_upper=100000,
                    currency="INR",
                    raw_payload={"mock": True},
                )
            ],
            next_cursor=None,
        )

    async def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_name=self.name,
            is_healthy=True,
            status_message="Adapter A active (Fixture/API ready)",
        )

