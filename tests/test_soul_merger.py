"""Tests for Soul Merger."""
import pytest

from openmemo_openclaw.soul_merger import (
    merge_soul,
    merge_into_messages,
    extract_user_rules,
    RULES_SECTION_MARKER,
)


class TestMergeSoul:
    def test_empty_rules(self):
        prompt = "You are a helpful assistant."
        result = merge_soul(prompt, "")
        assert result == prompt

    def test_basic_merge(self):
        prompt = "You are a helpful assistant."
        rules = "## Memory Rules\n1. Use memory."
        result = merge_soul(prompt, rules)
        assert "You are a helpful assistant." in result
        assert "## Memory Rules" in result
        assert RULES_SECTION_MARKER in result

    def test_idempotent_merge(self):
        prompt = "You are a helpful assistant."
        rules = "1. Use memory."
        r1 = merge_soul(prompt, rules)
        r2 = merge_soul(r1, rules)
        assert r2.count(RULES_SECTION_MARKER) == 2
        assert r2.count("1. Use memory.") == 1

    def test_preserves_original(self):
        prompt = "System: You are an AI.\nBe helpful."
        rules = "1. Check memory first."
        result = merge_soul(prompt, rules)
        assert "System: You are an AI." in result
        assert "Be helpful." in result
        assert "Check memory first." in result


class TestMergeIntoMessages:
    def test_empty_rules(self):
        msgs = [{"role": "user", "content": "Hello"}]
        result = merge_into_messages(msgs, "")
        assert result == msgs

    def test_merge_with_system(self):
        msgs = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ]
        result = merge_into_messages(msgs, "1. Use memory.")
        assert "1. Use memory." in result[0]["content"]
        assert result[0]["role"] == "system"
        assert result[1]["content"] == "Hi"

    def test_merge_without_system(self):
        msgs = [{"role": "user", "content": "Hi"}]
        result = merge_into_messages(msgs, "1. Use memory.")
        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert "1. Use memory." in result[0]["content"]

    def test_does_not_mutate_original(self):
        msgs = [
            {"role": "system", "content": "Original"},
            {"role": "user", "content": "Hi"},
        ]
        original_content = msgs[0]["content"]
        merge_into_messages(msgs, "1. Rule.")
        assert msgs[0]["content"] == original_content


class TestExtractUserRules:
    def test_found(self):
        assert extract_user_rules("Always check memory before acting") is not None

    def test_not_found(self):
        assert extract_user_rules("You are a helpful assistant.") is None

    def test_case_insensitive(self):
        assert extract_user_rules("Use Memory when available") is not None
