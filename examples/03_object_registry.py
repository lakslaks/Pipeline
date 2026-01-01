"""
03_object_registry.py
Demonstrates using object registry to call module functions like `math.sqrt`.
"""

from my_pipeline.executor import PipelineExecutor
import math
import asyncio

steps = [
    {"name": "square_root", "action": "math#sqrt", "args": [49], "publish": "result"},
    {"name": "print_result", "action": "builtins#print", "args": ["${result}"]}
]

executor = PipelineExecutor(name="registry", steps=steps, custom_objects={"math": math})
asyncio.run(executor.execute())
