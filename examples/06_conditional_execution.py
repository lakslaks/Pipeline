"""
06_conditional_execution.py
Demonstrates use of `when` to control conditional step execution.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio

steps = [
    {"name": "always", "action": "builtins#print", "args": ["Always runs"]},
    {"name": "only_if_true", "action": "builtins#print", "args": ["x > 10 triggered!"], "when": "${x} > 10"}
]

executor = PipelineExecutor(name="conditional", steps=steps)
executor.context["x"] = 15  # Try changing to 5 to skip
asyncio.run(executor.execute())
