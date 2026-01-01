"""
18_staged_event_trigger.py
Demonstrates event-driven execution using StagedExecutor.
"""

from my_pipeline.staged_executor import StagedExecutor
import asyncio

steps = [
    {"name": "start", "action": "builtins#print", "args": ["Start!"], "trigger": "go"},
    {"name": "followup", "on": "go", "action": "builtins#print", "args": ["Triggered!"]}
]

executor = StagedExecutor(name="staged", steps=steps)
asyncio.run(executor.execute())
