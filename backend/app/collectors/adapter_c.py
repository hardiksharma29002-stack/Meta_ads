"""Adapter C: Proprietary Playwright Headless Chromium Scraper.

Built for emergency contingency capability.
STRICTLY FEATURE-FLAGGED OFF by default (ADR-0001, ADR-0002) until legal sign-off.
"""

from app.collectors.base import (
    Capabilities,
    SearchQuery,
    RawAd,
    Page,
    Money,
    AdapterHealth,
)
from app.core.config import settings
from app.core.errors import AdAtlasException
from app.core.logging import logger


class AdapterC_PlaywrightUI:
    name = "adapter_c"
    schema_version = 1

    def __init__(self, enabled: bool = settings.ADAPTER_C_ENABLED):
        self.enabled = enabled

    def capabilities(self) -> Capabilities:
        return Capabilities(
            commercial_ads=True,
            political_ads=False,
            spend_ranges=False,
            page_based_query=True,
            keyword_query=True,
            only_new_ads=False,
            max_page_size=50,
        )

    def estimate_cost(self, q: SearchQuery) -> Money:
        # Proxy bandwidth and compute cost estimate (~$0.50/1k pages)
        return Money(amount=round((q.limit / 1000.0) * 0.50, 4), currency="USD")

    async def search(self, q: SearchQuery, cursor: str | None = None) -> Page[RawAd]:
        if not self.enabled:
            logger.error("adapter_c_invocation_rejected", reason="Feature flag OFF per ADR-0001")
            raise AdAtlasException(
                title="Adapter C Disabled",
                status_code=403,
                detail="Adapter C (Playwright UI scraper) is disabled. Legal sign-off in docs/COMPLIANCE_AND_LEGAL.md is required before activation.",
                type_uri="https://errors.adatlas.in/adapter-disabled",
            )
        # Placeholder for sandboxed Playwright session
        return Page(items=[], next_cursor=None)

    async def by_page(self, page_id: str, cursor: str | None = None, active_only: bool = True) -> Page[RawAd]:
        return await self.search(SearchQuery(city_slug="all", page_id=page_id, active_only=active_only), cursor)

    async def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_name=self.name,
            is_healthy=self.enabled,
            status_message="Adapter C built; Flagged OFF by default per compliance policy (ADR-0001)",
        )

