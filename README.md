# OpenMemo × OpenClaw Adapter

Cognitive Memory Backend for OpenClaw Agents.

OpenClaw runs as usual — just point memory backend to OpenMemo.

## Quick Start

### 1. Install

```bash
pip install openmemo openmemo-openclaw
```

### 2. Start OpenMemo Local Server

```bash
openmemo serve --port 8765
```

### 3. Configure OpenClaw

Create `openclaw.memory.yaml`:

```yaml
memory:
  backend: openmemo
  mode: local_api
  endpoint: http://127.0.0.1:8765
  injection_strategy: system
  conflict_policy: suppress
  max_injected_items: 3
```

### 4. Run OpenClaw

```bash
openclaw run
```

That's it. OpenClaw runs normally, with long-term memory powered by OpenMemo.

## Three Running Modes

### Auto (Recommended)

```yaml
memory:
  backend: openmemo
  mode: auto
```

Tries library → local_api → cloud. Zero config needed.

### Local API

```yaml
memory:
  backend: openmemo
  mode: local_api
  endpoint: http://127.0.0.1:8765
```

Best for: debugging, cross-language agents, stable deployment.

### Library (Zero Server)

```yaml
memory:
  backend: openmemo
  mode: library
```

No separate process. Lowest latency. Best user experience.
Requires `pip install openmemo`.

### Cloud

```yaml
memory:
  backend: openmemo
  mode: cloud
  endpoint: https://api.openmemo.ai
  api_key: your-api-key
```

Best for: multi-device sync, hosted environments, shared memory.

## How It Works

```
openclaw run
    │
    ▼
Plugin Init (load config, health check)
    │
    ▼
Hook Registration
  • on_user_message
  • on_agent_response
  • on_tool_call
  • on_task_complete
    │
    ▼
Each inference round:
  1. Recall (query → /agent/context → memory context)
  2. Scene detection (auto: coding/debug/deployment/research/...)
  3. Inject into prompt (system or user_prefix strategy)
  4. Agent runs inference
  5. Async write (event → queue → OpenMemo)
```

## Python API

### Plugin (Recommended)

```python
from openmemo_openclaw import OpenClawMemoryPlugin

# From YAML config
plugin = OpenClawMemoryPlugin.from_yaml("openclaw.memory.yaml")

# Or from dict
plugin = OpenClawMemoryPlugin.from_dict({
    "memory": {
        "mode": "auto",
        "injection_strategy": "system",
    }
})

# Hook lifecycle events
plugin.on_message("deploy my app")
plugin.on_response("Using Docker to deploy", tools=["docker"])
plugin.on_tool_call("docker", "build succeeded")
plugin.on_task_complete("Deployed app via Docker")

# Inject memory into message list
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "How should I deploy?"},
]
messages = plugin.inject_context(messages, query="deploy application")

# Or get raw context string
context = plugin.get_context("deployment tools")

# Or enhance a single prompt
prompt = plugin.enhance_prompt("Which language should I use?")
```

### Adapter (Advanced)

```python
from openmemo_openclaw import OpenMemoAdapter, AdapterConfig

config = AdapterConfig(
    backend="local_api",
    endpoint="http://localhost:8765",
    persona_id="python_architect",
    injection_strategy="system",
    conflict_policy="suppress",
    max_injected_items=5,
    max_memory_tokens=200,
)
adapter = OpenMemoAdapter(config)

# Same API as plugin, plus:
adapter.set_files(["src/app.py", "Dockerfile"])  # scene hint
adapter.recall_ranked("deployment", scene="deployment")  # ranked results
```

### Async Mode

```python
adapter = OpenMemoAdapter(config, async_mode=True)
await adapter.start_async()

adapter.on_user_message("deploy my app")  # non-blocking write

await adapter.stop_async()
```

## Health Check

On startup, the adapter automatically verifies:

- Endpoint reachable
- `/memory/search` responds
- `/agent/context` responds

If anything fails:

```
OpenMemo backend unavailable: cannot connect to http://127.0.0.1:8765
```

Disable with `health_check: false` in config.

## Structured Logs

```
[openmemo] adapter initialized (backend=local_api, mode=sync)
[openmemo] scene=deployment type=observation queued_write content="deploy my Python app..."
[openmemo] recall query="deploy" scene=deployment hit=2
[openmemo] injected 2 memories into system prompt
[openmemo] adapter closed
```

Enable with standard Python logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
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
├── Transformer (event normalization)
├── Scene Mapper (auto-detect scene)
├── Ranker (recency + semantic + scene scoring)
├── Injector (system / user_prefix injection)
└── Queue Worker (async write with retry)
│
▼
Memory Client (provider selection + fallback)
├── Library Provider (direct SDK)
├── Local API Provider (HTTP → openmemo serve)
└── Cloud API Provider (HTTP → api.openmemo.ai)
│
▼
OpenMemo Memory Core
```

## Features

- Scene-aware recall (coding, debug, deployment, research, file_analysis, web_search)
- Recency-aware ranking: `semantic×0.6 + recency×0.25 + scene×0.15`
- Conflict suppression (newer memory wins)
- Async memory writes with retry + exponential backoff
- Provider auto-fallback: library → local_api → cloud
- Cold start handling (skip injection when memory empty)
- Health check on init
- Structured logging

## License

MIT
