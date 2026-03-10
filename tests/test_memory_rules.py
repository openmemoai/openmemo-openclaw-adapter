"""Tests for Memory Rules Engine."""
import os
import tempfile
import pytest

from openmemo_openclaw.memory_rules import (
    MemoryRulesEngine,
    DEFAULT_MEMORY_RULES,
    RULES_VERSION,
    load_rules,
)
from openmemo_openclaw.config import AdapterConfig


class TestMemoryRulesEngine:
    def test_default_init(self):
        engine = MemoryRulesEngine()
        assert engine.enabled is True
        assert engine.version == RULES_VERSION
        assert engine.rule_count == 8
        assert "OpenMemo Memory Rules" in engine.rules_text

    def test_disabled(self):
        engine = MemoryRulesEngine(enabled=False)
        assert engine.enabled is False
        assert engine.rules_text == ""
        assert engine.rule_count == 0

    def test_custom_rules(self):
        engine = MemoryRulesEngine()
        engine.add_rule("9. Custom rule for testing.")
        assert "Custom rule" in engine.rules_text
        assert engine.status["custom_rules"] == 1

    def test_enable_disable(self):
        engine = MemoryRulesEngine()
        engine.disable()
        assert engine.enabled is False
        engine.enable()
        assert engine.enabled is True

    def test_update_rules(self):
        engine = MemoryRulesEngine()
        engine.update_rules("## New Rules\nversion: 2.0\n1. Only rule.", "2.0")
        assert engine.version == "2.0"
        assert "Only rule" in engine.rules_text
        assert engine.rule_count == 1

    def test_status(self):
        engine = MemoryRulesEngine()
        s = engine.status
        assert s["enabled"] is True
        assert s["version"] == RULES_VERSION
        assert s["rule_count"] == 8
        assert s["custom_rules"] == 0

    def test_from_file(self):
        content = "## Custom Rules\nversion: 3.0\n1. Rule one.\n2. Rule two."
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            path = f.name
        try:
            engine = MemoryRulesEngine.from_file(path)
            assert engine.version == "3.0"
            assert engine.rule_count == 2
            assert "Rule one" in engine.rules_text
        finally:
            os.unlink(path)

    def test_from_file_not_found(self):
        engine = MemoryRulesEngine.from_file("/nonexistent/path.md")
        assert engine.enabled is True
        assert engine.rule_count == 8

    def test_from_file_disabled(self):
        engine = MemoryRulesEngine.from_file("/nonexistent/path.md", enabled=False)
        assert engine.enabled is False


class TestLoadRules:
    def test_load_default(self):
        config = AdapterConfig()
        engine = load_rules(config)
        assert engine.enabled is True
        assert engine.rule_count == 8

    def test_load_disabled_mode(self):
        config = AdapterConfig(memory_rules_mode="disabled")
        engine = load_rules(config)
        assert engine.enabled is False

    def test_load_disabled_flag(self):
        config = AdapterConfig(auto_memory_rules=False)
        engine = load_rules(config)
        assert engine.enabled is False

    def test_load_from_file(self):
        content = "## File Rules\nversion: 1.5\n1. File rule."
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            path = f.name
        try:
            config = AdapterConfig(rules_file=path)
            engine = load_rules(config)
            assert engine.enabled is True
            assert engine.version == "1.5"
        finally:
            os.unlink(path)
