"""
17_template_executor.py
Demonstrates calling templates by name using TemplateExecutor.
"""

from my_pipeline.template_executor import TemplateExecutor
import asyncio

TEMPLATES = {
    "welcome": [
        {"name": "hello", "action": "builtins#print", "args": ["Hello from Template"]}
    ]
}

executor = TemplateExecutor(name="templater", template_registry=TEMPLATES)
executor.run_template("welcome")
