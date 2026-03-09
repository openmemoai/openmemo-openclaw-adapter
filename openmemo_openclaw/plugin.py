"""
OpenClaw Memory Plugin v2.0 — automatic cognitive memory for OpenClaw agents.

install → run → memory works automatically.

Usage:
    plugin = OpenClawMemoryPlugin()  # auto mode, everything enabled

    # Lifecycle hooks (auto-registered)
    plugin.on_message("deploy my app")
    plugin.on_response("Using Docker", tools=["docker"])
    plugin.on_tool_call("docker", "build succeeded")
    plugin.on_task_complete("Deployed via Docker")

    # Pre-check: has this task been done before?
    result = plugin.pre_check("deploy my app")

    # Inject memory into messages
    messages = plugin.inject_context(messages, query="deploy")
"""

import logging
from typing import List, Optional

from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.config import AdapterConfig
from openmemo_openclaw.pre_check import PreCheckResult

logger = logging.getLogger("openmemo_openclaw")


class OpenClawMemoryPlugin:
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
                         task_id: str = "", status: str = "success"):
        self._adapter.on_task_complete(
            summary, tools=tools, task_id=task_id, status=status,
        )

    def pre_check(self, query: str, scene: str = "",
                  tools: list = None) -> PreCheckResult:
        return self._adapter.pre_check(query, scene=scene, tools=tools)

    def inject_context(self, messages: List[dict], query: str,
                       scene: str = "",
                       include_pre_check: bool = True) -> List[dict]:
        return self._adapter.inject_context(
            messages, query, scene=scene, include_pre_check=include_pre_check,
        )

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
