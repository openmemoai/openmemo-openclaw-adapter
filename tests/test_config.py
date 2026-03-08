import pytest
from openmemo_openclaw.config import AdapterConfig


class TestAdapterConfig:
    def test_defaults(self):
        config = AdapterConfig()
        assert config.backend == "local_api"
        assert config.endpoint == "http://localhost:8765"
        assert config.persona_id == "default"
        assert config.injection_strategy == "system"
        assert config.conflict_policy == "suppress"
        assert config.max_injected_items == 5
        assert config.max_memory_tokens == 200
        assert config.recall_limit == 5
        assert config.queue_max_retry == 3

    def test_namespace(self):
        config = AdapterConfig(persona_id="python_architect")
        assert config.namespace == "openclaw/python_architect"

    def test_default_namespace(self):
        config = AdapterConfig()
        assert config.namespace == "openclaw/default"

    def test_custom_platform(self):
        config = AdapterConfig(agent_platform="myagent", persona_id="coder")
        assert config.namespace == "myagent/coder"

    def test_from_dict(self):
        data = {
            "memory": {
                "backend": "library",
                "persona_id": "tester",
                "max_injected_items": 3,
            }
        }
        config = AdapterConfig.from_dict(data)
        assert config.backend == "library"
        assert config.persona_id == "tester"
        assert config.max_injected_items == 3

    def test_from_dict_flat(self):
        data = {
            "backend": "cloud_api",
            "persona_id": "researcher",
        }
        config = AdapterConfig.from_dict(data)
        assert config.backend == "cloud_api"
        assert config.persona_id == "researcher"

    def test_scene_override(self):
        config = AdapterConfig(scene_override="debug")
        assert config.scene_override == "debug"
