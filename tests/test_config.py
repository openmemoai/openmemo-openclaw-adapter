import pytest
from openmemo_openclaw.config import AdapterConfig


class TestAdapterConfig:
    def test_defaults(self):
        config = AdapterConfig()
        assert config.backend == "auto"
        assert config.endpoint == "http://localhost:8765"
        assert config.persona_id == "default"
        assert config.injection_strategy == "system"
        assert config.conflict_policy == "suppress"
        assert config.auto_write is True
        assert config.auto_recall is True
        assert config.max_injected_items == 5
        assert config.max_memory_tokens == 200
        assert config.recall_limit == 5
        assert config.queue_max_retry == 3
        assert config.health_check is True

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

    def test_from_dict_mode_alias(self):
        data = {"memory": {"mode": "local_api", "persona_id": "tester"}}
        config = AdapterConfig.from_dict(data)
        assert config.backend == "local_api"

    def test_from_dict_mode_cloud_alias(self):
        data = {"memory": {"mode": "cloud"}}
        config = AdapterConfig.from_dict(data)
        assert config.backend == "cloud_api"

    def test_from_dict_mode_overrides_backend(self):
        data = {"memory": {"mode": "library", "backend": "cloud_api"}}
        config = AdapterConfig.from_dict(data)
        assert config.backend == "library"

    def test_scene_override(self):
        config = AdapterConfig(scene_override="debug")
        assert config.scene_override == "debug"

    def test_health_check_disabled(self):
        config = AdapterConfig(health_check=False)
        assert config.health_check is False

    def test_from_dict_health_check(self):
        data = {"memory": {"health_check": False}}
        config = AdapterConfig.from_dict(data)
        assert config.health_check is False

    def test_auto_write_from_dict(self):
        data = {"memory": {"auto_write": False}}
        config = AdapterConfig.from_dict(data)
        assert config.auto_write is False

    def test_auto_recall_from_dict(self):
        data = {"memory": {"auto_recall": False}}
        config = AdapterConfig.from_dict(data)
        assert config.auto_recall is False

    def test_auto_defaults_true(self):
        data = {"memory": {"backend": "library"}}
        config = AdapterConfig.from_dict(data)
        assert config.auto_write is True
        assert config.auto_recall is True
