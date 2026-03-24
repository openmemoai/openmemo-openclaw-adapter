# OpenMemo × OpenClaw Adapter

**Turn OpenClaw Agents into Persistent, Memory-Driven Collaborators**

Most AI agents today are stateless.

They forget:
- what tasks they already completed
- what decisions were made
- what tools worked before
- what the user prefers

So they repeat work. They redo the same tasks. They waste tokens and time.

**OpenMemo fixes this.**

OpenMemo adds a persistent memory layer to OpenClaw that allows agents to:
- remember past actions
- reuse successful workflows
- avoid duplicate work
- accumulate long-term knowledge

After installing OpenMemo, your OpenClaw agents stop behaving like stateless chatbots and start behaving like **long-term collaborators**.

---

## What OpenMemo Adds to OpenClaw

Installing the adapter enables:

### Persistent Memory

Agents remember:
- preferences
- past tasks
- decisions
- workflows
- observations

Example memory:

```
User switched from Flask to FastAPI
Scene: coding
Type: decision
Confidence: 0.92
```

### Task Deduplication

Before executing a task, OpenMemo checks whether it has already been done.

```
task: deploy backend
fingerprint: deployment|backend|docker-compose
status: success
```

If the task was already completed, the agent can **reuse**, **skip**, or **continue** — instead of repeating work.

### Scene-Aware Memory

OpenMemo detects the current working scene:
- `coding`
- `debugging`
- `research`
- `deployment`
- `analysis`

and retrieves only the most relevant memories.

### Structured Knowledge

OpenMemo stores atomic memory cells, not raw chat logs.

Instead of:
> long messy conversation history

it stores:

```
"Backend deployed using Docker Compose"
Scene: deployment
Type: task_execution
```

This dramatically improves recall quality.

### Automatic Memory

OpenMemo automatically extracts memory from:
- conversations
- tool calls
- task completions
- decision changes

No manual tagging required.

### Memory Inspector

OpenMemo includes a visual dashboard where you can see:
- what the agent remembers
- how memory is ranked
- how much token cost is saved

---

## Why This Matters

Modern agent frameworks like OpenClaw, LangGraph, CrewAI, and AutoGPT are enabling developers to build increasingly complex AI workflows.

But most agents still rely on short-term chat context. That means:
- no long-term learning
- no task reuse
- no accumulated experience

**OpenMemo introduces a memory infrastructure layer designed specifically for agents.**

---

## Architecture

OpenMemo sits between the agent and the LLM.

```
User / Agent Interaction
        │
        ▼
   Memory Capture
   (conversation, tool calls, tasks)
        │
        ▼
  OpenMemo Memory Engine
        │
  ┌─────┼─────┐
  │     │     │
Recall Ranking Dedup
  │     │     │
  └─────┴─────┘
        │
        ▼
  Context Injection
        │
        ▼
   LLM Reasoning
```

### Local-First Design

OpenMemo is local-first by default. All memory operations run locally.

```
Agent
  ↓
OpenMemo Local Server
  ↓
Memory Store
```

Cloud services are optional.

Benefits:
- **Privacy** — all data stays local
- **Low latency** — no network round trips
- **No external dependencies** — works offline

---

## Automatic Memory Rules

Installing OpenMemo also activates **Memory Rules**.

These rules guide the agent to properly use memory:

1. Prefer OpenMemo memory over raw conversation history.
2. Before executing any task, check if the task was already completed.
3. If a task already succeeded, reuse or skip it.
4. After meaningful task completion, write structured memory back to OpenMemo.

These rules are injected through a **merged soul context**, ensuring consistent memory behavior.

---

## Memory Inspector

OpenMemo includes a built-in **Memory Inspector Dashboard**.

The inspector shows:

| Metric | Description |
|--------|-------------|
| Memory Cells | Total structured memories stored |
| Tokens Saved | Token cost reduction from memory reuse |
| Recall Confidence | Quality score of memory retrieval |
| System Status | Health of memory infrastructure |
| Scene Dynamics | Current detected scene and confidence |

Users can override the detected scene if needed.

### Memory Stream

Real-time memory entries with ranking:

```
User switched from Flask to FastAPI
Scene: coding
Rank Score: 0.92
```

This makes the memory system **transparent and explainable**.

---

## Example Workflows

### Coding Agent

**Without OpenMemo:**

```
User: deploy backend
Agent: builds image → deploys

(later...)

User: deploy backend again
Agent: repeats everything from scratch
```

**With OpenMemo:**

```
User: deploy backend
Agent: deploys using Docker Compose → memory stored

(later...)

User: deploy backend again
Agent: detects prior deployment → reuses workflow
```

### Research Agent

Agent remembers:
> User prefers academic papers over blog posts

Future research queries prioritize papers automatically.

### DevOps Agent

Agent remembers:
> Production deployments use Kubernetes

Future deployment tasks follow the correct workflow automatically.

---

## Multi-Agent Memory (Upcoming)

OpenMemo also enables collaborative memory for multi-agent systems.

Memory is organized into three layers:

### Private Memory

Per-agent knowledge.

```
planner_agent/private
coder_agent/private
```

### Shared Task Memory

Agents working on the same task share memory.

```
task_123/shared
```

Stores: task goals, completed steps, execution results.

### Team Knowledge Memory

Long-term shared knowledge.

```
team/default
```

Stores: project conventions, reusable workflows.

---

## What Makes OpenMemo Different

| Feature | Chat History | RAG | **OpenMemo** |
|---------|-------------|-----|-------------|
| Persistent Memory | ❌ | ❌ | ✅ |
| Task Deduplication | ❌ | ❌ | ✅ |
| Scene Awareness | ❌ | ❌ | ✅ |
| Decision Tracking | ❌ | ❌ | ✅ |
| Memory Inspector | ❌ | ❌ | ✅ |

**OpenMemo is not just memory storage. It is agent memory infrastructure.**

---

## Installation — Complete Setup (3 Steps)

  ### ⚠️ Important

  **This is an OpenClaw plugin / ClawHub skill.**
  **It is NOT a Python package.**

  ❌ Do NOT run:
  ```bash
  pip install openmemo-openclaw
  ```

  ---

  ### 🧱 Requirements

  | Requirement | Version |
  |-------------|---------|
  | Node.js | >= 18 |
  | npm / npx | included with Node.js |
  | Python | >= 3.9 |
  | OpenClaw | installed |

  ---

  ### Step 1 — Install the skill (ClawHub)

  📦 ClawHub page: [clawhub.ai/openmemoai/openmemo-clawhub-skill](https://clawhub.ai/openmemoai/openmemo-clawhub-skill)

  ```bash
  npx clawhub@latest install openmemo-clawhub-skill
  ```

  Expected output:
  ```
  √ OK. Installed openmemo-clawhub-skill
  ```

  > ⚠️ This installs the skill plugin only. The memory adapter is NOT running yet.
  > You must complete Step 2 before memory will work.

  ---

  ### Step 2 — Install and start the OpenMemo adapter

  Run these once in a separate terminal:

  **macOS / Linux:**
  ```bash
  pip install openmemo openmemo-openclaw
  openmemo serve
  ```

  **Windows (PowerShell):**
  ```powershell
  python -m pip install openmemo openmemo-openclaw
  python -m openmemo serve
  ```

  Keep `openmemo serve` running in the background.

  ---

  ### Step 3 — Start OpenClaw

  Start your OpenClaw agent normally. The skill detects the adapter automatically and activates Memory Mode.

  You will see memory tools become available:
  - `check_task_memory`
  - `recall_memory`
  - `write_memory`

  ---

  ### Why two separate install steps?

  | Step | Component | What it does |
  |------|-----------|-------------|
  | `npx clawhub install` | Skill (OpenClaw plugin) | Registers the skill in OpenClaw workspace |
  | `pip install openmemo` | Adapter (Python backend) | Installs the local memory engine |
  | `openmemo serve` | Adapter server | Runs the local memory API on port 8765 |

  The skill and adapter are two separate components. Both must be running.

  ---

  ### Manual Install (Alternative)

  📂 Source: [github.com/openmemoai/openmemo-clawhub-skill](https://github.com/openmemoai/openmemo-clawhub-skill)

  ```bash
  git clone https://github.com/openmemoai/openmemo-clawhub-skill.git
  cd openmemo-clawhub-skill
  npm install
  ```

  Then register in `~/.openclaw/openclaw.json`:
  ```json
  {
    "plugins": ["./path/to/openmemo-clawhub-skill"]
  }
  ```

  ---

  ### 🛠️ Troubleshooting

  #### Windows: `npm error canceled`

  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

  Then retry the install command.

  #### Skill installed but memory not working

  Most likely cause: Step 2 is missing. The adapter is not running.

  Run:
  ```bash
  openmemo serve
  ```

  Then restart OpenClaw.

  #### Common errors

  | Error | Cause | Fix |
  |-------|-------|-----|
  | `npm error canceled` (Windows) | PowerShell execution policy | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
  | Memory tools not available | Adapter not running | Run `openmemo serve`, restart OpenClaw |
  | `openmemo` not recognized (Windows) | Scripts not in PATH | Use `python -m openmemo serve` |
  | `npx` not recognized | Node.js not installed | Install from [nodejs.org](https://nodejs.org/) |
  | Rate limit exceeded | ClawHub API limit | Wait a few seconds and retry |

  ---

  ## Vision

We believe future software will be built around persistent AI agents.

These agents need:
- long-term memory
- shared knowledge
- explainable reasoning
- reusable workflows

**OpenMemo is building the memory infrastructure for AI agents.**

---

## Contributing

We welcome contributions from the community.

If you're interested in building the future of agent memory infrastructure, join us.

---

## License

MIT

---

**Built with [OpenMemo](https://github.com/openmemoai/openmemo) — The Memory Infrastructure for AI Agents.**
