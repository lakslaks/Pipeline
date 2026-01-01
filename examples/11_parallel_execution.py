"""
11_parallel_execution.py
Runs steps in parallel with a join strategy.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio
import time

def delay(msg, sec):
    time.sleep(sec)
    return f"{msg} done after {sec}s"

class Delayer:
    @staticmethod
    def delay(msg, sec):
        return delay(msg, sec)

steps = [
    {
        "parallel": {
            "join": "all",
            "steps": [
                {"name": "p1", "action": "self#delay", "args": ["A", 2]},
                {"name": "p2", "action": "self#delay", "args": ["B", 1]},
                {"name": "p3", "action": "self#delay", "args": ["C", 3]}
            ]
        }
    }
]

executor = PipelineExecutor(name="parallel", steps=steps, custom_objects={"self": Delayer()})
asyncio.run(executor.execute())
