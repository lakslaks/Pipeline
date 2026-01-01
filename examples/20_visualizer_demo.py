"""
20_visualizer_demo.py
Creates a Mermaid diagram of the pipeline structure using the visualizer plugin.
"""

from my_pipeline.executor import PipelineExecutor
from my_pipeline.plugins import visualizer

steps = [
    {"name": "step1", "action": "builtins#print", "args": ["Step 1"], "trigger": "next"},
    {"name": "step2", "on": "next", "action": "builtins#print", "args": ["Step 2"]}
]

executor = PipelineExecutor(name="vis-demo", steps=steps)
visualizer.design_view(steps)
