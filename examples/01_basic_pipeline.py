"""
01_basic_pipeline.py
Demonstrates a single-step pipeline using a built-in function.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio

steps = [
    {"name": "hello", "action": "builtins#print", "args": ["Hello, Pipeline!"]}
]

executor = PipelineExecutor(name="basic", steps=steps)
asyncio.run(executor.execute())
