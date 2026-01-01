"""
template_executor.py

Extends PipelineExecutor to support named pipeline templates.
Enables calling specific pipelines by name without exposing internal step details.
"""

import asyncio
from typing import Dict, Any, Optional, Union, List
from .executor import PipelineExecutor


class TemplateExecutor(PipelineExecutor):
    def __init__(self,
                 template_registry: Dict[str, List[Dict[str, Any]]],
                 skip_compile: bool = False,
                 **kwargs):
        """
        Args:
            template_registry (dict): Dictionary of named pipeline templates.
            skip_compile (bool): Skip loading steps if set to True.
            kwargs: Passed to base PipelineExecutor.
        """
        self.template_registry = template_registry
        steps = None if skip_compile else kwargs.get("steps")
        super().__init__(steps=steps, **kwargs)

    def run_template(self, template_name: str,
                     context: Optional[Dict[str, Any]] = None,
                     **run_kwargs):
        """
        Execute a template pipeline by name.

        Args:
            template_name (str): Key from the template_registry.
            context (dict, optional): Execution context to inject.
            run_kwargs: Passed to `execute()`.
        """
        if template_name not in self.template_registry:
            raise ValueError(f"Template '{template_name}' not found")

        self.compiled_steps = self._compile_steps(self.template_registry[template_name])
        self.context = context or {}
        return asyncio.run(self.execute(**run_kwargs))

    def list_templates(self):
        """Returns list of registered pipeline names."""
        return list(self.template_registry.keys())
