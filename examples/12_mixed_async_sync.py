"""
12_mixed_async_sync.py
Mixes asynchronous and synchronous step functions.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio

async def async_task():
    await asyncio.sleep(0.5)
    return "Async Done"

def sync_task():
    return "Sync Done"

class Combo:
    @staticmethod
    async def async_task():
        return await async_task()

    @staticmethod
    def sync_task():
        return sync_task()

steps = [
    {"name": "sync", "action": "self#sync_task", "publish": "a"},
    {"name": "async", "action": "self#async_task", "publish": "b"},
    {"name": "display", "action": "builtins#print", "args": ["${a}, ${b}"]}
]

executor = PipelineExecutor(name="mixed", steps=steps, custom_objects={"self": Combo()})
asyncio.run(executor.execute())
