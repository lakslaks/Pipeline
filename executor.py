"""
executor.py

Defines the core PipelineExecutor class for executing step-based pipelines.
Supports:
- Serial and parallel steps
- Conditional execution via `when`
- Publishing values to shared context
- Step-level timeout, logging, and debug options
"""

# executor.py

import asyncio
import logging
import inspect
from typing import Any, Dict, List, Optional, Union

from .arg_resolver import resolve_args, resolve_func
from .conditionals import evaluate_condition
from .controllers import get_effective_timeout
from .io_utils import load_steps_from_source
from .step_runner import run_serial_step, run_parallel_block
from . import utils


class PipelineExecutor:
    def __init__(self, name: str,
                 steps: Optional[Union[str, List[Dict[str, Any]]]] = None,
                 custom_objects: Optional[Union[Dict[str, Any], List[Any]]] = None,
                 execution_controllers: Optional[Dict[str, Any]] = None,
                 debug: bool = False,
                 logger: Optional[logging.Logger] = None):
        self.name = name
        self.debug = debug
        self.logger = logger
        self.context: Dict[str, Any] = {}
        self.context_lock = asyncio.Lock()
        self.object_registry: Dict[str, Any] = {
            "re": __import__("re"),
            "builtins": __import__("builtins"),
            "os": __import__("os"),
            "operator": __import__("operator"),
            "utils": utils,
        }
        self._init_object_registry(custom_objects)
        self.compiled_steps: List[Dict[str, Any]] = []
        self._result: List[Any] = []

        self.controllers = execution_controllers or {}
        self.controllers.setdefault("timeout", None)
        self.controllers.setdefault("debug", debug)
        self.controllers.setdefault("log", logger)

        if steps:
            self.load_steps(steps)

    def _init_object_registry(self, custom_objs):
        if custom_objs is None:
            return
        if isinstance(custom_objs, dict):
            self.object_registry.update(custom_objs)
        elif isinstance(custom_objs, list):
            for obj in custom_objs:
                key = obj.__name__ if inspect.ismodule(obj) else obj.__class__.__name__
                self.object_registry[key] = obj

    def load_steps(self, steps):
        parsed = load_steps_from_source(steps)
        self.context.clear()
        self.compiled_steps = self._compile_steps(parsed)
        self._step_map = {step["name"]: step for step in self.compiled_steps if "name" in step}

    def _compile_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compiled = []
        for step in steps:
            # Handle parallel block
            if "parallel" in step:
                parallel_block = step["parallel"]
                # Recursively compile inner steps
                compiled_inner = self._compile_steps(parallel_block.get("steps", []))
                # Preserve other keys like join, retry, etc.
                compiled.append({
                    "parallel": {
                        **{k: v for k, v in parallel_block.items() if k != "steps"},
                        "steps": compiled_inner
                    }
                })
                print(compiled)
                continue
    
            # Normal step
            s = step.copy()
            action = s.get("action")
            if action:
                s["func"] = resolve_func(action, self.object_registry, s.get("decorate"))
            compiled.append(s)
        return compiled

    def _compile_steps3(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compiled = []
        for step in steps:
            if "parallel" in step:
                parallel_block = step["parallel"]
                compiled_inner = self._compile_steps(parallel_block.get("steps", []))
                compiled.append({
                    "parallel": {
                        **{k: v for k, v in parallel_block.items() if k != "steps"},
                        "steps": compiled_inner
                    }
                })
                continue
            compiled.append(compile_single_step(step, self.object_registry))
        return compiled

    async def execute(self, timeout: Optional[int] = None) -> None:
        async def run_pipeline():
            for step in self.compiled_steps:
                if isinstance(step, dict) and "parallel" in step:
                    await run_parallel_block(step["parallel"], self)
                else:
                    await run_serial_step(step, self)

        try:
            if timeout:
                await asyncio.wait_for(run_pipeline(), timeout=timeout)
            else:
                await run_pipeline()
        except asyncio.TimeoutError:
            msg = f"[TIMEOUT] Entire pipeline '{self.name}' exceeded {timeout}s"
            print(msg)
            if self.logger:
                self.logger.warning(msg)
    @property
    def result(self):
        return self._result

    @property
    def last(self):
        return self.result[-1] if self.result else None


def compile_single_step(step: Dict[str, Any], object_registry: Dict[str, Any]) -> Dict[str, Any]:
    if "parallel" in step:
        raise ValueError("compile_single_step does not support 'parallel' blocks directly.")
    s = step.copy()
    action = s.get("action")
    if action:
        s["func"] = resolve_func(action, object_registry, s.get("decorate"))
    return s

