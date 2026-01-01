"""
16_decorators_usage.py
Applies multiple decorators to a custom function.
"""

from my_pipeline.executor import PipelineExecutor
from my_pipeline.decorators import timed_step, step_logger
import asyncio

class Handler:
    @staticmethod
    @step_logger
    @timed_step
    def compute():
        return "42"

steps = [
    {"name": "calc", "action": "self#compute", "publish": "answer"},
    {"name": "echo", "action": "builtins#print", "args": ["Answer: ${answer}"]}
]

executor = PipelineExecutor(name="decorated", steps=steps, custom_objects={"self": Handler()})
asyncio.run(executor.execute())
