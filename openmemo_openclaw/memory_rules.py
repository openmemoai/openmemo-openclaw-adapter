"""
OpenMemo Memory Rules Engine — enforces memory behavior contracts.

Loads, manages, and provides memory rules that guide Agent behavior:
- When to use memory
- When to check task memory
- When to write memory
- How to handle conflicts

Rules are auto-loaded on adapter init and injected via the soul merger.
"""

import logging
from typing import Optional

logger = logging.getLogger("openmemo_openclaw")

RULES_VERSION = "1.0"

DEFAULT_MEMORY_RULES = """## OpenMemo Memory Rules
version: 1.0

When OpenMemo is enabled, follow these memory rules:

1. Prefer OpenMemo memory over raw conversation history when making decisions.

2. Before executing any task, check whether a similar task has already been completed, partially completed, or rejected.

3. If prior task memory indicates the same task has already succeeded, prefer reuse, skip, or continuation rather than repeating the task.

4. Treat the user's most recent instruction as higher priority than older memory.

5. After meaningful task completion, tool execution, or decision changes, write structured memory back to OpenMemo.

6. Use memory as short, structured, actionable knowledge rather than narrative chat history.

7. Avoid repeating tasks that have already been completed unless explicitly instructed.

8. When recalling memory, prioritize context relevant to the current scene and task."""


class MemoryRulesEngine:
    def __init__(self, rules_text: str = None, version: str = None,
                 enabled: bool = True):
        self._enabled = enabled
        self._version = version or RULES_VERSION
        self._rules = rules_text or DEFAULT_MEMORY_RULES if enabled else ""
        self._custom_rules: list = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def version(self) -> str:
        return self._version

    @property
    def rules_text(self) -> str:
        if not self._enabled:
            return ""
        parts = [self._rules]
        for cr in self._custom_rules:
            parts.append(cr)
        return "\n\n".join(parts)

    @property
    def rule_count(self) -> int:
        if not self._enabled:
            return 0
        lines = self._rules.strip().split("\n")
        return sum(1 for line in lines if line.strip() and line.strip()[0].isdigit())

    def add_rule(self, rule: str):
        self._custom_rules.append(rule)

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    def update_rules(self, new_rules: str, new_version: str = None):
        self._rules = new_rules
        if new_version:
            self._version = new_version
        logger.info("[openmemo] memory rules updated to version %s", self._version)

    @property
    def status(self) -> dict:
        return {
            "enabled": self._enabled,
            "version": self._version,
            "rule_count": self.rule_count,
            "custom_rules": len(self._custom_rules),
        }

    @classmethod
    def from_file(cls, path: str, enabled: bool = True) -> "MemoryRulesEngine":
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            version_line = [l for l in text.split("\n") if l.strip().startswith("version:")]
            ver = version_line[0].split(":", 1)[1].strip() if version_line else RULES_VERSION
            return cls(rules_text=text, version=ver, enabled=enabled)
        except FileNotFoundError:
            logger.warning("[openmemo] rules file not found: %s, using defaults", path)
            return cls(enabled=enabled)
        except Exception as e:
            logger.warning("[openmemo] failed to load rules from %s: %s", path, e)
            return cls(enabled=enabled)


def load_rules(config) -> MemoryRulesEngine:
    enabled = config.auto_memory_rules
    mode = config.memory_rules_mode

    if mode == "disabled" or not enabled:
        return MemoryRulesEngine(enabled=False)

    if mode not in ("merged_soul", "disabled"):
        logger.warning("[openmemo] unknown memory_rules_mode '%s', falling back to merged_soul", mode)

    version = getattr(config, "rules_version", RULES_VERSION)

    if hasattr(config, "rules_file") and config.rules_file:
        return MemoryRulesEngine.from_file(config.rules_file, enabled=True)

    return MemoryRulesEngine(enabled=True, version=version)
