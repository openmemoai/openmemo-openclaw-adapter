import pytest
from openmemo_openclaw.transformer import (
    transform_event,
    transform_user_message,
    transform_agent_response,
    transform_tool_call,
    transform_task_complete,
    extract_memory_content,
    infer_memory_type,
)


class TestTransformEvent:
    def test_basic_transform(self):
        event = transform_event("user_message", "hello world")
        assert event["type"] == "user_message"
        assert event["content"] == "hello world"
        assert event["timestamp"] > 0

    def test_empty_content_returns_empty(self):
        event = transform_event("user_message", "")
        assert event == {}

    def test_with_tools_and_metadata(self):
        event = transform_event(
            "tool_call", "docker build",
            tools=["docker"], task_id="deploy",
            session_id="s1", metadata={"key": "val"},
        )
        assert event["tools"] == ["docker"]
        assert event["task_id"] == "deploy"
        assert event["session_id"] == "s1"
        assert event["metadata"]["key"] == "val"

    def test_long_text_truncated(self):
        long_text = "x" * 1000
        event = transform_event("user_message", long_text)
        assert len(event["content"]) == 500

    def test_whitespace_cleaned(self):
        event = transform_event("user_message", "  hello   world  ")
        assert event["content"] == "hello world"


class TestTransformHelpers:
    def test_user_message(self):
        event = transform_user_message("deploy my app", session_id="s1")
        assert event["type"] == "user_message"
        assert event["session_id"] == "s1"

    def test_agent_response(self):
        event = transform_agent_response("using docker", tools=["docker"])
        assert event["type"] == "agent_response"
        assert event["tools"] == ["docker"]

    def test_tool_call(self):
        event = transform_tool_call("pytest", "3 passed")
        assert event["type"] == "tool_call"
        assert "pytest" in event["content"]

    def test_task_complete(self):
        event = transform_task_complete("Deployed successfully")
        assert event["type"] == "task_complete"


class TestExtractMemoryContent:
    def test_user_message(self):
        event = {"type": "user_message", "content": "hello"}
        assert extract_memory_content(event) == "User: hello"

    def test_agent_response_with_tools(self):
        event = {"type": "agent_response", "content": "done", "tools": ["docker"]}
        result = extract_memory_content(event)
        assert "Agent: done" in result
        assert "docker" in result

    def test_agent_response_no_tools(self):
        event = {"type": "agent_response", "content": "done", "tools": []}
        assert extract_memory_content(event) == "Agent: done"

    def test_empty_content(self):
        event = {"type": "user_message", "content": ""}
        assert extract_memory_content(event) is None


class TestInferMemoryType:
    def test_preference(self):
        event = {"type": "user_message", "content": "I prefer Python"}
        assert infer_memory_type(event) == "preference"

    def test_decision(self):
        event = {"type": "agent_response", "content": "decided to use Flask"}
        assert infer_memory_type(event) == "decision"

    def test_constraint(self):
        event = {"type": "user_message", "content": "must use HTTPS always"}
        assert infer_memory_type(event) == "constraint"

    def test_task_complete_is_fact(self):
        event = {"type": "task_complete", "content": "deployed app"}
        assert infer_memory_type(event) == "fact"

    def test_default_is_observation(self):
        event = {"type": "agent_response", "content": "running tests now"}
        assert infer_memory_type(event) == "observation"
