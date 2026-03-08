import os
import tempfile
import pytest
from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.config import AdapterConfig


@pytest.fixture
def adapter():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    config = AdapterConfig(
        backend="library",
        db_path=path,
        persona_id="test_agent",
        health_check=False,
    )
    a = OpenMemoAdapter(config)
    yield a
    a.close()
    os.remove(path)


class TestAdapter:
    def test_on_user_message(self, adapter):
        adapter.on_user_message("deploy my app")
        assert adapter.stats["worker_stats"]["written"] == 1

    def test_on_agent_response(self, adapter):
        adapter.on_agent_response("using docker", tools=["docker"])
        assert adapter.stats["worker_stats"]["written"] == 1

    def test_on_tool_call(self, adapter):
        adapter.on_tool_call("pytest", "3 passed")
        assert adapter.stats["worker_stats"]["written"] == 1

    def test_on_task_complete(self, adapter):
        adapter.on_task_complete("Deployed successfully")
        assert adapter.stats["worker_stats"]["written"] == 1

    def test_recall_empty(self, adapter):
        result = adapter.recall("something")
        assert isinstance(result, list)

    def test_recall_after_write(self, adapter):
        adapter.on_user_message("User prefers Python backend")
        result = adapter.recall("Python")
        assert isinstance(result, list)

    def test_build_prompt_cold_start(self, adapter):
        prompt = adapter.build_prompt("hello world")
        assert "hello world" in prompt

    def test_build_prompt_with_memory(self, adapter):
        adapter.on_user_message("User prefers Python backend")
        prompt = adapter.build_prompt("which language?")
        assert "which language?" in prompt

    def test_scene_override(self, adapter):
        adapter.scene_override("deployment")
        adapter.on_user_message("test message")
        assert adapter.stats["current_scene"] == "deployment"

    def test_session_management(self, adapter):
        adapter.set_session("session_123")
        adapter.set_task("task_456")
        assert adapter.stats["session_id"] == "session_123"

    def test_namespace(self, adapter):
        assert adapter.stats["namespace"] == "openclaw/test_agent"

    def test_context_manager(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        config = AdapterConfig(backend="library", db_path=path, health_check=False)
        with OpenMemoAdapter(config) as a:
            a.on_user_message("test")
        os.remove(path)

    def test_multiple_events(self, adapter):
        adapter.on_user_message("deploy app")
        adapter.on_agent_response("using docker", tools=["docker"])
        adapter.on_tool_call("docker", "build succeeded")
        adapter.on_task_complete("Deployed via Docker")
        assert adapter.stats["worker_stats"]["written"] == 4

    def test_get_context_cold_start(self, adapter):
        context = adapter.get_context("hello")
        assert context is None

    def test_list_scenes_after_writes(self, adapter):
        adapter.scene_override("coding")
        adapter.on_user_message("wrote some Python code")
        scenes = adapter.list_scenes()
        assert isinstance(scenes, list)

    def test_inject_context_cold_start(self, adapter):
        messages = [{"role": "user", "content": "hello"}]
        result = adapter.inject_context(messages, query="hello")
        assert result == messages

    def test_inject_context_with_memory(self, adapter):
        adapter.on_user_message("User prefers Python backend")
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "which language?"},
        ]
        result = adapter.inject_context(messages, query="Python language")
        assert len(result) >= 2

    def test_set_files(self, adapter):
        adapter.set_files(["src/app.py", "Dockerfile"])
        adapter.on_user_message("deploy this app")
        assert adapter.stats["current_scene"] in ("deployment", "coding", "general")
