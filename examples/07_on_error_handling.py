"""
07_on_error_handling.py
Demonstrates recovery using `on-error`.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio

def fail():
    raise ValueError("Intentional failure.")

class Failer:
    @staticmethod
    def fail():
        return fail()

steps = [
    {"name": "risky", "action": "self#fail", "on-error": "fallback"},
    {"name": "fallback", "action": "builtins#print", "args": ["Recovered from error."]}
]

executor = PipelineExecutor(name="error-handling", steps=steps, custom_objects={"self": Failer()})
asyncio.run(executor.execute())
