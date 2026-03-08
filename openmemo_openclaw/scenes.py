"""
Scene mapper — auto-detects scene from task context, tools, and file paths.
"""

from typing import Optional

SCENE_RULES = {
    "coding": {
        "tools": ["code_editor", "write_file", "create_file", "edit"],
        "files": ["src/", ".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp"],
        "keywords": ["implement", "code", "function", "class", "refactor", "variable"],
    },
    "debug": {
        "tools": ["pytest", "test", "debugger", "lint", "ruff"],
        "files": ["test_", "_test.", ".test.", "spec.", "tests/"],
        "keywords": ["debug", "fix", "error", "bug", "traceback", "exception", "fail", "test"],
    },
    "deployment": {
        "tools": ["docker", "kubectl", "terraform", "ansible", "ssh", "deploy"],
        "files": ["Dockerfile", "docker-compose", ".yml", "k8s/", "deploy/"],
        "keywords": ["deploy", "docker", "container", "kubernetes", "server", "production"],
    },
    "research": {
        "tools": ["web_search", "search", "browser", "fetch"],
        "files": [],
        "keywords": ["search", "research", "find", "lookup", "documentation", "learn"],
    },
    "file_analysis": {
        "tools": ["read_file", "list_files", "cat", "grep"],
        "files": [".log", ".csv", ".json", ".xml"],
        "keywords": ["analyze", "read", "parse", "inspect", "review"],
    },
    "web_search": {
        "tools": ["web_search", "browse", "scrape"],
        "files": [],
        "keywords": ["google", "web", "url", "website", "browse"],
    },
}


class SceneMapper:
    def __init__(self):
        self._override: Optional[str] = None

    def scene_override(self, scene: str):
        self._override = scene

    def clear_override(self):
        self._override = None

    def detect(self, task_name: str = "", tools: list = None,
               file_paths: list = None, prompt: str = "") -> str:
        if self._override:
            return self._override

        scores = {}
        for scene, rules in SCENE_RULES.items():
            score = 0.0

            if tools:
                for tool in tools:
                    tool_lower = tool.lower()
                    for pattern in rules["tools"]:
                        if pattern in tool_lower:
                            score += 2.0

            if file_paths:
                for fp in file_paths:
                    fp_lower = fp.lower()
                    fname = fp_lower.rsplit("/", 1)[-1]
                    for pattern in rules["files"]:
                        if pattern in fp_lower:
                            bonus = 2.0 if fname.startswith(pattern) else 1.5
                            score += bonus

            text = f"{task_name} {prompt}".lower()
            for kw in rules["keywords"]:
                if kw in text:
                    score += 1.0

            if score > 0:
                scores[scene] = score

        if not scores:
            return "general"

        return max(scores, key=scores.get)


def detect_scene(task_name: str = "", tools: list = None,
                 file_paths: list = None, prompt: str = "") -> str:
    mapper = SceneMapper()
    return mapper.detect(task_name, tools, file_paths, prompt)
