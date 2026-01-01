"""
08_before_after_hooks.py
Demonstrates custom hooks before and after each step.
"""

from my_pipeline.executor import PipelineExecutor
import asyncio

def before(name, step, ctx):
    print(f"==> Starting step: {name}")

def after(name, step, ctx, result):
    print(f"<== Finished step: {name} with result: {result}")

steps = [
    {"name": "hooked", "action": "builtins#print", "args": ["Inside hooked step."]}
]

executor = PipelineExecutor(name="hooks", steps=steps, execution_controllers={
    "before": before,
    "after": after
})
asyncio.run(executor.execute())
