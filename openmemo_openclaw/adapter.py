"""
OpenMemo Adapter — main orchestrator for OpenClaw memory integration.

Coordinates: transformer → scene mapper → async write → recall → ranker → injector
"""

import logging
from typing import List, Optional

from openmemo_openclaw.config import AdapterConfig
from openmemo_openclaw.memory_client import MemoryClient
from openmemo_openclaw.transformer import (
    transform_user_message,
    transform_agent_response,
    transform_tool_call,
    transform_task_complete,
    extract_memory_content,
    infer_memory_type,
)
from openmemo_openclaw.scenes import SceneMapper
from openmemo_openclaw.ranker import rank_memories
from openmemo_openclaw.injector import inject_context, build_prompt
from openmemo_openclaw.queue_worker import SyncMemoryWorker, AsyncMemoryWorker

logger = logging.getLogger("openmemo_openclaw.adapter")


class OpenMemoAdapter:
    """
    Main adapter class connecting OpenClaw to OpenMemo.

    Usage:
        config = AdapterConfig(persona_id="python_architect")
        adapter = OpenMemoAdapter(config)

        adapter.on_user_message("deploy my app")
        context = adapter.recall("deploy application", scene="deployment")
        prompt = adapter.build_prompt("deploy my app")

    Async mode (recommended for agent loops):
        async with OpenMemoAdapter(config, async_mode=True) as adapter:
            await adapter.start_async()
            adapter.on_user_message("deploy my app")
    """

    def __init__(self, config: AdapterConfig = None, async_mode: bool = False):
        self._config = config or AdapterConfig()
        self._client = MemoryClient(self._config)
        self._scene_mapper = SceneMapper()
        self._session_id = ""
        self._current_task_id = ""
        self._current_scene = ""
        self._current_files: list = []
        self._async_mode = async_mode

        if async_mode:
            self._async_worker = AsyncMemoryWorker(
                write_fn=self._do_write,
                max_retry=self._config.queue_max_retry,
                backoff_base=self._config.queue_backoff_base,
            )
            self._sync_worker = None
        else:
            self._sync_worker = SyncMemoryWorker(
                write_fn=self._do_write,
                max_retry=self._config.queue_max_retry,
                backoff_base=self._config.queue_backoff_base,
            )
            self._async_worker = None

        if self._config.scene_override:
            self._scene_mapper.scene_override(self._config.scene_override)

    async def start_async(self):
        if self._async_worker:
            await self._async_worker.start()

    async def stop_async(self):
        if self._async_worker:
            await self._async_worker.stop()

    def set_session(self, session_id: str):
        self._session_id = session_id

    def set_task(self, task_id: str):
        self._current_task_id = task_id

    def set_files(self, file_paths: list):
        self._current_files = file_paths or []

    def scene_override(self, scene: str):
        self._scene_mapper.scene_override(scene)
        self._current_scene = scene

    def clear_scene_override(self):
        self._scene_mapper.clear_override()

    def on_user_message(self, message: str, task_id: str = ""):
        event = transform_user_message(
            message,
            session_id=self._session_id,
            task_id=task_id or self._current_task_id,
        )
        if event:
            self._process_event(event)

    def on_agent_response(self, response: str, tools: list = None,
                          task_id: str = ""):
        event = transform_agent_response(
            response,
            tools=tools,
            session_id=self._session_id,
            task_id=task_id or self._current_task_id,
        )
        if event:
            self._process_event(event)

    def on_tool_call(self, tool_name: str, tool_output: str = "",
                     task_id: str = ""):
        event = transform_tool_call(
            tool_name,
            tool_output,
            session_id=self._session_id,
            task_id=task_id or self._current_task_id,
        )
        if event:
            self._process_event(event)

    def on_task_complete(self, summary: str, tools: list = None,
                         task_id: str = ""):
        event = transform_task_complete(
            summary,
            tools=tools,
            session_id=self._session_id,
            task_id=task_id or self._current_task_id,
        )
        if event:
            self._process_event(event)

    def recall(self, query: str, scene: str = "",
               limit: int = None) -> List[str]:
        effective_scene = scene or self._current_scene
        memories = self._client.recall_context(
            query=query,
            scene=effective_scene,
            limit=limit or self._config.recall_limit,
        )
        return memories

    def recall_ranked(self, query: str, scene: str = "",
                      limit: int = None) -> List[dict]:
        effective_scene = scene or self._current_scene
        results = self._client.search_memory(
            query=query,
            scene=effective_scene,
            limit=limit or self._config.recall_limit,
        )

        ranked = rank_memories(
            results,
            current_scene=effective_scene,
            conflict_policy=self._config.conflict_policy,
        )

        return ranked[:self._config.max_injected_items]

    def get_context(self, query: str, scene: str = "") -> Optional[str]:
        memories = self.recall(query, scene=scene)
        if not memories:
            return None

        return inject_context(
            memories,
            strategy=self._config.injection_strategy,
            max_items=self._config.max_injected_items,
            max_tokens=self._config.max_memory_tokens,
        )

    def build_prompt(self, user_prompt: str, query: str = "",
                     scene: str = "") -> str:
        effective_query = query or user_prompt
        memories = self.recall(effective_query, scene=scene)

        return build_prompt(
            original_prompt=user_prompt,
            memory_context=memories,
            strategy=self._config.injection_strategy,
            max_items=self._config.max_injected_items,
            max_tokens=self._config.max_memory_tokens,
        )

    def list_scenes(self) -> List[str]:
        return self._client.list_scenes()

    @property
    def stats(self) -> dict:
        worker_stats = (
            self._async_worker.stats if self._async_worker
            else self._sync_worker.stats if self._sync_worker
            else {}
        )
        return {
            "namespace": self._config.namespace,
            "backend": self._config.backend,
            "session_id": self._session_id,
            "current_scene": self._current_scene,
            "async_mode": self._async_mode,
            "worker_stats": worker_stats,
        }

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _process_event(self, event: dict):
        scene = self._detect_scene(event)
        self._current_scene = scene

        content = extract_memory_content(event)
        if not content:
            return

        memory_type = infer_memory_type(event)

        payload = {
            "content": content,
            "scene": scene,
            "memory_type": memory_type,
            "metadata": {
                "task_id": event.get("task_id", ""),
                "session_id": event.get("session_id", ""),
                "event_type": event.get("type", ""),
            },
        }

        if self._async_mode and self._async_worker:
            self._async_worker.enqueue_sync(payload)
        elif self._sync_worker:
            self._sync_worker.write(payload)

    def _detect_scene(self, event: dict) -> str:
        tools = event.get("tools", [])
        task_id = event.get("task_id", "")
        content = event.get("content", "")

        return self._scene_mapper.detect(
            task_name=task_id,
            tools=tools,
            file_paths=self._current_files,
            prompt=content,
        )

    def _do_write(self, payload: dict):
        self._client.write_memory(
            content=payload["content"],
            scene=payload.get("scene", ""),
            memory_type=payload.get("memory_type", "observation"),
            metadata=payload.get("metadata", {}),
        )
