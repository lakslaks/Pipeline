"""
10_global_timeout_and_policy.py
Demonstrates global timeout and debug policies.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio
import time

def sleeper():
    time.sleep(2)
    return "zzz..."

class Sleeper:
    @staticmethod
    def sleeper():
        return sleeper()

steps = [
    {"name": "quick", "action": "builtins#print", "args": ["Quick run"]},
    {"name": "sleep", "action": "self#sleeper"}
]

executor = PipelineExecutor(name="policy-demo", steps=steps, custom_objects={"self": Sleeper()}, execution_controllers={
    "timeout": 3,
    "debug": True
})
asyncio.run(executor.execute())
