"""
OpenClaw Memory Plugin — lifecycle hooks that connect to OpenMemoAdapter.

The plugin is intentionally thin — it only hooks lifecycle events
and delegates all memory logic to the adapter.

Usage with YAML config:
    plugin = OpenClawMemoryPlugin.from_yaml("openclaw.memory.yaml")

Usage with dict config:
    plugin = OpenClawMemoryPlugin.from_dict({
        "memory": {
            "backend": "openmemo",
            "mode": "local_api",
            "endpoint": "http://127.0.0.1:8765",
        }
    })

Minimal usage:
    plugin = OpenClawMemoryPlugin()  # auto mode, tries library first
"""

import logging
from typing import List, Optional

from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.config import AdapterConfig

logger = logging.getLogger("openmemo_openclaw")


class OpenClawMemoryPlugin:
    """
    Plugin that hooks into OpenClaw agent lifecycle.

    Designed for zero-friction integration: install, configure, run.
    """

    def __init__(self, config: AdapterConfig = None,
                 persona_id: str = "default",
                 endpoint: str = "http://localhost:8765",
                 backend: str = "auto",
                 async_mode: bool = False,
                 **kwargs):
        if config is None:
            config = AdapterConfig(
                persona_id=persona_id,
                endpoint=endpoint,
                backend=backend,
                **{k: v for k, v in kwargs.items()
                   if hasattr(AdapterConfig, k)},
            )
        self._adapter = OpenMemoAdapter(config, async_mode=async_mode)
        self._config = config

    @classmethod
    def from_yaml(cls, path: str, **kwargs) -> "OpenClawMemoryPlugin":
        config = AdapterConfig.from_yaml(path)
        return cls(config=config, **kwargs)

    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> "OpenClawMemoryPlugin":
        config = AdapterConfig.from_dict(data)
        return cls(config=config, **kwargs)

    def set_session(self, session_id: str):
        self._adapter.set_session(session_id)

    def set_task(self, task_id: str):
        self._adapter.set_task(task_id)

    def set_files(self, file_paths: list):
        self._adapter.set_files(file_paths)

    def scene_override(self, scene: str):
        self._adapter.scene_override(scene)

    def on_message(self, message: str, task_id: str = ""):
        self._adapter.on_user_message(message, task_id=task_id)

    def on_response(self, response: str, tools: list = None,
                    task_id: str = ""):
        self._adapter.on_agent_response(response, tools=tools, task_id=task_id)

    def on_tool_call(self, tool_name: str, output: str = "",
                     task_id: str = ""):
        self._adapter.on_tool_call(tool_name, output, task_id=task_id)

    def on_task_complete(self, summary: str, tools: list = None,
                         task_id: str = ""):
        self._adapter.on_task_complete(summary, tools=tools, task_id=task_id)

    def inject_context(self, messages: List[dict], query: str,
                       scene: str = "") -> List[dict]:
        return self._adapter.inject_context(messages, query, scene=scene)

    def enhance_prompt(self, user_prompt: str, scene: str = "") -> str:
        return self._adapter.build_prompt(user_prompt, scene=scene)

    def recall(self, query: str, scene: str = "") -> list:
        return self._adapter.recall(query, scene=scene)

    def get_context(self, query: str, scene: str = "") -> Optional[str]:
        return self._adapter.get_context(query, scene=scene)

    def list_scenes(self) -> list:
        return self._adapter.list_scenes()

    async def start_async(self):
        await self._adapter.start_async()

    async def stop_async(self):
        await self._adapter.stop_async()

    @property
    def stats(self) -> dict:
        return self._adapter.stats

    def close(self):
        self._adapter.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
