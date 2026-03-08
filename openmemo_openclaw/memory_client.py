"""
Unified memory client — selects provider based on config.

Provider priority: library → local_api → cloud_api
When backend="auto", tries each provider in order and falls back on failure.
"""

import logging
from typing import List

from openmemo_openclaw.config import AdapterConfig

logger = logging.getLogger("openmemo_openclaw.memory_client")


class MemoryClient:
    def __init__(self, config: AdapterConfig):
        self._config = config
        self._provider = self._create_provider(config)

    def _create_provider(self, config: AdapterConfig):
        backend = config.backend

        if backend == "auto":
            return self._create_with_fallback(config)

        if backend == "library":
            return self._try_library(config)

        if backend == "cloud_api":
            from openmemo_openclaw.providers.cloud_api import CloudAPIProvider
            return CloudAPIProvider(
                base_url=config.cloud_url,
                api_key=config.api_key,
            )

        from openmemo_openclaw.providers.local_api import LocalAPIProvider
        return LocalAPIProvider(endpoint=config.endpoint)

    def _create_with_fallback(self, config: AdapterConfig):
        provider = self._try_library(config)
        if provider:
            logger.info("Using library provider (direct SDK)")
            return provider

        try:
            from openmemo_openclaw.providers.local_api import LocalAPIProvider
            provider = LocalAPIProvider(endpoint=config.endpoint)
            logger.info("Using local API provider at %s", config.endpoint)
            return provider
        except Exception:
            pass

        from openmemo_openclaw.providers.cloud_api import CloudAPIProvider
        logger.info("Using cloud API provider at %s", config.cloud_url)
        return CloudAPIProvider(
            base_url=config.cloud_url,
            api_key=config.api_key,
        )

    def _try_library(self, config: AdapterConfig):
        try:
            from openmemo_openclaw.providers.library import LibraryProvider
            return LibraryProvider(db_path=config.db_path)
        except ImportError:
            logger.debug("OpenMemo library not available, trying next provider")
            return None
        except Exception as e:
            logger.debug("Library provider failed: %s", e)
            return None

    def write_memory(self, content: str, scene: str = "",
                     memory_type: str = "observation",
                     confidence: float = 0.8,
                     metadata: dict = None) -> str:
        return self._provider.write_memory(
            content=content,
            scene=scene,
            memory_type=memory_type,
            agent_id=self._config.namespace,
            confidence=confidence,
            metadata=metadata,
        )

    def recall_context(self, query: str, scene: str = "",
                       limit: int = None) -> List[str]:
        return self._provider.recall_context(
            query=query,
            scene=scene,
            agent_id=self._config.namespace,
            limit=limit or self._config.recall_limit,
        )

    def search_memory(self, query: str, scene: str = "",
                      limit: int = 10) -> List[dict]:
        return self._provider.search_memory(
            query=query,
            scene=scene,
            agent_id=self._config.namespace,
            limit=limit,
        )

    def list_scenes(self) -> List[str]:
        return self._provider.list_scenes(
            agent_id=self._config.namespace,
        )

    def close(self):
        if hasattr(self._provider, 'close'):
            self._provider.close()
