import pytest
from openmemo_openclaw.injector import (
    inject_context,
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
