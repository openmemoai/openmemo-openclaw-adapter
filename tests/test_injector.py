import pytest
from openmemo_openclaw.injector import (
    inject_context,
    inject_into_messages,
    format_system_injection,
    format_user_prefix,
    build_prompt,
)


class TestInjectContext:
    def test_empty_memories(self):
        assert inject_context([]) is None

    def test_system_strategy(self):
        result = inject_context(["memory 1", "memory 2"], strategy="system")
        assert "Relevant memory:" in result
        assert "1. memory 1" in result
        assert "2. memory 2" in result

    def test_user_prefix_strategy(self):
        result = inject_context(["memory 1"], strategy="user_prefix")
        assert "[Memory Context]" in result
        assert "1. memory 1" in result

    def test_max_items(self):
        memories = [f"item {i}" for i in range(10)]
        result = inject_context(memories, max_items=3)
        assert "3." in result
        assert "4." not in result

    def test_max_tokens(self):
        memories = ["word " * 100, "short"]
        result = inject_context(memories, max_tokens=50)
        assert result is not None


class TestInjectIntoMessages:
    def test_empty_memories_returns_original(self):
        messages = [{"role": "user", "content": "hello"}]
        result = inject_into_messages(messages, [])
        assert result == messages

    def test_system_strategy_appends_to_existing(self):
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "deploy my app"},
        ]
        result = inject_into_messages(messages, ["User uses Docker"], strategy="system")
        assert len(result) == 2
        assert "You are helpful." in result[0]["content"]
        assert "Relevant memory:" in result[0]["content"]
        assert "User uses Docker" in result[0]["content"]

    def test_system_strategy_creates_system_msg(self):
        messages = [
            {"role": "user", "content": "deploy my app"},
        ]
        result = inject_into_messages(messages, ["User uses Docker"], strategy="system")
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert "Relevant memory:" in result[0]["content"]

    def test_user_prefix_strategy(self):
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "deploy my app"},
        ]
        result = inject_into_messages(messages, ["User uses Docker"], strategy="user_prefix")
        assert len(result) == 2
        assert "[Memory Context]" in result[1]["content"]
        assert "deploy my app" in result[1]["content"]

    def test_does_not_mutate_original(self):
        messages = [
            {"role": "system", "content": "Original"},
            {"role": "user", "content": "Hello"},
        ]
        result = inject_into_messages(messages, ["memory"], strategy="system")
        assert messages[0]["content"] == "Original"
        assert "memory" in result[0]["content"]

    def test_max_items_respected(self):
        messages = [{"role": "user", "content": "test"}]
        memories = [f"item {i}" for i in range(10)]
        result = inject_into_messages(messages, memories, max_items=2)
        content = result[0]["content"]
        assert "1." in content
        assert "2." in content
        assert "3." not in content


class TestBuildPrompt:
    def test_with_system_injection(self):
        result = build_prompt(
            "deploy my app",
            ["User uses Docker"],
            strategy="system",
        )
        assert "Relevant memory:" in result
        assert "deploy my app" in result

    def test_with_user_prefix(self):
        result = build_prompt(
            "deploy my app",
            ["User uses Docker"],
            strategy="user_prefix",
        )
        assert "[Memory Context]" in result
        assert "deploy my app" in result

    def test_empty_context(self):
        result = build_prompt("hello", [])
        assert result == "hello"

    def test_cold_start(self):
        result = build_prompt("hello", [], strategy="system")
        assert result == "hello"
        assert "Relevant memory:" not in result


class TestFormatHelpers:
    def test_format_system(self):
        result = format_system_injection(["test memory"])
        assert "Relevant memory:" in result

    def test_format_user_prefix(self):
        result = format_user_prefix(["test memory"])
        assert "[Memory Context]" in result
