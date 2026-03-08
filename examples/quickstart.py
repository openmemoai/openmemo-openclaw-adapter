"""
OpenMemo × OpenClaw Adapter — Quick Start Demo

Run:
    pip install openmemo openmemo-openclaw
    python examples/quickstart.py

This demo shows the full lifecycle:
    1. Plugin initialization
    2. Event hooks (user_message → agent_response → tool_call → task_complete)
    3. Memory recall with scene detection
    4. Context injection into message list
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

from openmemo_openclaw import OpenClawMemoryPlugin, AdapterConfig

config = AdapterConfig(
    backend="library",
    persona_id="demo_agent",
    injection_strategy="system",
    conflict_policy="suppress",
    max_injected_items=3,
    health_check=False,
)

plugin = OpenClawMemoryPlugin(config=config)

print("=" * 60)
print("OpenMemo × OpenClaw — Quick Start Demo")
print("=" * 60)

print("\n--- Round 1: User asks to deploy ---")

plugin.on_message("deploy my Python app to production")
plugin.on_response(
    "I'll use Docker to containerize your Python app and deploy it.",
    tools=["docker"],
)
plugin.on_tool_call("docker", "Successfully built image: myapp:latest")
plugin.on_task_complete(
    "Deployed Python app via Docker to production",
    tools=["docker", "ssh"],
)

print("\n--- Round 2: User asks about deployment (recall should fire) ---")

messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "How should I deploy my next app?"},
]

enhanced = plugin.inject_context(messages, query="deploy application")

print("\nOriginal messages:")
for msg in messages:
    print(f"  [{msg['role']}] {msg['content'][:80]}")

print("\nEnhanced messages (with memory):")
for msg in enhanced:
    print(f"  [{msg['role']}] {msg['content'][:120]}")

print("\n--- Stats ---")
stats = plugin.stats
print(f"  Backend: {stats['backend']}")
print(f"  Namespace: {stats['namespace']}")
print(f"  Scene: {stats['current_scene']}")
print(f"  Writes: {stats['worker_stats'].get('written', 0)}")

plugin.close()
print("\nDone.")
