"""
21_event_fanout_replay.py
Demonstrates one event (`ready`) triggering multiple parallel steps
and generates a post-execution Mermaid diagram via visualizer.execution_view.
"""

from my_pipeline.staged_executor import StagedExecutor
from my_pipeline.plugins import visualizer
import asyncio

logs = []

def record(name, result=None, error=None, fired=None):
    logs.append({
        "name": name,
        "result": result,
        "error": str(error) if error else None,
        "fired_events": fired or []
    })

steps = [
    {
        "name": "bootstrap",
        "action": "builtins#print",
        "args": ["Starting..."],
        "trigger": "ready"
    },
    {
        "name": "alpha",
        "on": "ready",
        "action": "builtins#print",
        "args": ["Alpha triggered"],
        "publish": "result_alpha"
    },
    {
        "name": "beta",
        "on": "ready",
        "action": "builtins#print",
        "args": ["Beta triggered"],
        "publish": "result_beta"
    },
    {
        "name": "gamma",
        "on": "ready",
        "action": "builtins#print",
        "args": ["Gamma triggered"],
        "publish": "result_gamma"
    }
]

class ReplayExecutor(StagedExecutor):
    async def _run_step(self, step):
        name = step.get("name")
        result, error, fired = None, None, []

        try:
            await super()._run_step(step)
            if step.get("publish") and self.publish_triggers_event:
                fired.append(step["publish"])
            if step.get("trigger"):
                fired.append(step["trigger"])
            result = self.context.get(step.get("publish"))
        except Exception as e:
            error = e
        record(name, result=result, error=error, fired=fired)

# Execute and visualize
executor = ReplayExecutor(name="fanout", steps=steps)
asyncio.run(executor.execute())

visualizer.execution_view(logs, output_path="pipeline_execution_fanout.mmd")
