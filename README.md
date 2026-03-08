# OpenMemo × OpenClaw Adapter

Cognitive Memory Backend for OpenClaw Agents.

## Install

```bash
pip install openmemo-openclaw
```

## Quick Start

```python
from openmemo_openclaw import OpenClawMemoryPlugin

plugin = OpenClawMemoryPlugin(
    persona_id="python_architect",
    backend="library",  # or "local_api", "cloud_api"
)

# Hook lifecycle events
plugin.on_message("deploy my app")
plugin.on_response("Using Docker to deploy", tools=["docker"])
plugin.on_tool_call("docker", "build succeeded")
plugin.on_task_complete("Deployed app via Docker")

# Enhance prompts with memory
prompt = plugin.enhance_prompt("Which language should I use?")
# → includes: "User prefers Python backend"

# Direct recall
memories = plugin.recall("deployment tools")
```

## Configuration

```python
from openmemo_openclaw import AdapterConfig

config = AdapterConfig(
    backend="local_api",              # library | local_api | cloud_api
    endpoint="http://localhost:8765",  # Local API server
    persona_id="python_architect",
    injection_strategy="system",      # system | user_prefix
    conflict_policy="suppress",
    max_injected_items=5,
    max_memory_tokens=200,
)
```

## Architecture

```
OpenClaw Agent
│
▼
OpenClaw Plugin (lifecycle hooks)
│
▼
OpenMemo Adapter (orchestration)
│
▼
OpenMemo Memory Core (storage + recall)
```

## Features

- Scene-aware recall (coding, debug, deployment, research)
- Recency-aware ranking
- Conflict suppression
- Async memory writes with retry
- Cold start handling
- System / user_prefix prompt injection

## License

MIT
