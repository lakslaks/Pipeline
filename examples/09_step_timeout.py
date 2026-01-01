"""
09_step_timeout.py
Demonstrates use of a step-level timeout.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio
import time

def slow_fn():
    time.sleep(3)
    return "done"

class Waiter:
    @staticmethod
    def slow_fn():
        return slow_fn()

steps = [
    {"name": "slow_step", "action": "self#slow_fn", "timeout": 1},
    {"name": "followup", "action": "builtins#print", "args": ["Finished!"]}
]

executor = PipelineExecutor(name="timeout-demo", steps=steps, custom_objects={"self": Waiter()})
asyncio.run(executor.execute())
