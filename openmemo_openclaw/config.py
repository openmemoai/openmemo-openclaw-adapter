"""
Adapter configuration with sensible defaults.

Supports three modes:
  - auto: try library → local_api → cloud (recommended)
  - local_api: force local API server
  - library: direct SDK (no server needed)
  - cloud: force cloud API

v2.0: auto_write and auto_recall enabled by default.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AdapterConfig:
    backend: str = "auto"
    endpoint: str = "http://localhost:8765"
    agent_platform: str = "openclaw"
    persona_id: str = "default"
    instance_id: str = ""

    injection_strategy: str = "system"
    conflict_policy: str = "suppress"

    auto_write: bool = True
    auto_recall: bool = True

    max_injected_items: int = 5
    max_memory_tokens: int = 200
    recall_limit: int = 5

    queue_max_retry: int = 3
    queue_backoff_base: float = 0.5

    scene_override: Optional[str] = None

    db_path: str = "openmemo.db"
    cloud_url: str = "https://api.openmemo.ai"
    api_key: Optional[str] = None

    health_check: bool = True

    @property
    def namespace(self) -> str:
        return f"{self.agent_platform}/{self.persona_id}"

    @classmethod
    def from_dict(cls, data: dict) -> "AdapterConfig":
        memory = data.get("memory", data)
        mode = memory.get("mode", memory.get("backend", "auto"))
        if mode == "cloud":
            mode = "cloud_api"
        return cls(
            backend=mode,
            endpoint=memory.get("endpoint", "http://localhost:8765"),
            agent_platform=memory.get("agent_platform", "openclaw"),
            persona_id=memory.get("persona_id", "default"),
            instance_id=memory.get("instance_id", ""),
            injection_strategy=memory.get("injection_strategy", "system"),
            conflict_policy=memory.get("conflict_policy", "suppress"),
            auto_write=memory.get("auto_write", True),
            auto_recall=memory.get("auto_recall", True),
            max_injected_items=memory.get("max_injected_items", 5),
            max_memory_tokens=memory.get("max_memory_tokens", 200),
            recall_limit=memory.get("recall_limit", 5),
            queue_max_retry=memory.get("queue_max_retry", 3),
            queue_backoff_base=memory.get("queue_backoff_base", 0.5),
            scene_override=memory.get("scene_override"),
            db_path=memory.get("db_path", "openmemo.db"),
            cloud_url=memory.get("cloud_url", "https://api.openmemo.ai"),
            api_key=memory.get("api_key"),
            health_check=memory.get("health_check", True),
        )

    @classmethod
    def from_yaml(cls, path: str) -> "AdapterConfig":
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
