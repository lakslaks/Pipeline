"""
05_queue_interaction.py
Demonstrates reading a value from a Python Queue inside a step.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio
from queue import Queue

q = Queue()
q.put("Message from queue!")

def dequeue():
    return q.get()

class QueueOps:
    @staticmethod
    def dequeue():
        return dequeue()

steps = [
    {"name": "read_queue", "action": "self#dequeue", "publish": "msg"},
    {"name": "show_msg", "action": "builtins#print", "args": ["${msg}"]}
]

executor = PipelineExecutor(name="queue-example", steps=steps, custom_objects={"self": QueueOps()})
asyncio.run(executor.execute())
