"""
19_trigger_chaining.py
Uses trigger to cascade a chain of dependent steps.
"""

from my_pipeline.staged_executor import StagedExecutor
import asyncio

steps = [
    {"name": "a", "action": "builtins#print", "args": ["A"], "trigger": "x"},
    {"name": "b", "on": "x", "action": "builtins#print", "args": ["B"], "trigger": "y"},
    {"name": "c", "on": "y", "action": "builtins#print", "args": ["C"]}
]

executor = StagedExecutor(name="trigger-chain", steps=steps)
asyncio.run(executor.execute())
