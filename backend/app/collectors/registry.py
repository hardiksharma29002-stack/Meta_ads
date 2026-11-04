"""Collector Adapter Registry & Factory."""

from typing import Dict
from app.collectors.base import AdSourceAdapter
from app.collectors.adapter_a import AdapterA_OfficialAPI
from app.collectors.adapter_b import AdapterB_ManagedProvider
from app.collectors.adapter_c import AdapterC_PlaywrightUI
from app.core.errors import NotFoundError


class AdapterRegistry:
    def __init__(self):
        self._adapters: Dict[str, AdSourceAdapter] = {
            "adapter_a": AdapterA_OfficialAPI(),
            "adapter_b": AdapterB_ManagedProvider(),
            "adapter_c": AdapterC_PlaywrightUI(),
        }

    def get_adapter(self, name: str) -> AdSourceAdapter:
        adapter = self._adapters.get(name.lower())
        if not adapter:
            raise NotFoundError("Collector Adapter", name)
        return adapter

    def list_adapters(self) -> list[str]:
        return list(self._adapters.keys())


adapter_registry = AdapterRegistry()

