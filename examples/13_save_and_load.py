"""
13_save_and_load.py
Shows saving and reloading a pipeline executor using pickle.
"""

from my_pipeline.executor import PipelineExecutor
from my_pipeline.io_utils import save_executor_state, load_executor_state
import asyncio

steps = [
    {"name": "msg", "action": "builtins#print", "args": ["Saving now..."]}
]

executor = PipelineExecutor(name="saver", steps=steps)
save_executor_state(executor, "saved_executor.pkl")

reloaded = load_executor_state("saved_executor.pkl")
asyncio.run(reloaded.execute())
