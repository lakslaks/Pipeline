"""
02_publishing_variables.py
Demonstrates use of `publish` and referencing values via `${}` in a later step.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio

steps = [
    {"name": "generate_number", "action": "builtins#str", "args": [123], "publish": "my_number"},
    {"name": "echo", "action": "builtins#print", "args": ["Number is ${my_number}"]}
]

executor = PipelineExecutor(name="publish-vars", steps=steps)
asyncio.run(executor.execute())
