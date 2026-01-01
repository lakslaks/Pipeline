"""
arg_resolver.py

Resolves function arguments and callable references based on pipeline context and step definitions.
Supports:
- ${var} substitution from context
- obj#method function resolution
- Decorator application via `decorate`
"""

import inspect
from typing import Any, Dict, List, Tuple, Union
from . import decorators

def resolve_args(step: Dict[str, Any], context: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Resolves *args and **kwargs from a unified 'args' or 'input' field.

    Args:
        step (dict): Step definition.
        context (dict): Shared pipeline context.

    Returns:
        tuple: Positional args list, keyword args dict.
    """
    args, kwargs = [], {}

    val = step.get("args") or step.get("input")

    if isinstance(val, dict):
        args = [resolve_arg(v, context) for v in val.pop("__args__", [])]
        kwargs = {k: resolve_arg(v, context) for k, v in val.items()}
    elif isinstance(val, (list, tuple)):
        args = [resolve_arg(v, context) for v in val]
    elif isinstance(val, str):
        args = [resolve_arg(val, context)]
    elif val is not None:
        raise TypeError(f"Invalid input type: {type(val).__name__}. Must be dict, list, tuple, or str.")

    # Include extra top-level keys as keyword arguments (if not reserved)
    for k, v in step.items():
        if k not in {
            "name", "action", "args", "input", "publish", "when",
            "on-success", "on-error", "timeout", "skip_hooks", "func", "decorate", "trigger", "on"
        }:
            kwargs[k] = resolve_arg(v, context)

    return args, kwargs

def resolve_arg(v: Any, context: Dict[str, Any]) -> Any:
    """
    Resolves a single value using context if it matches ${var} format.

    Args:
        v (any): Input value
        context (dict): Context store

    Returns:
        Resolved value
    """
    if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
        return context.get(v[2:-1])
    return v

def resolve_func(action: Union[str, Any], registry: Dict[str, Any], decorators_list: List[Union[str, Dict]] = None):
    """
    Resolves a callable from string or callable reference and applies decorators.

    Args:
        action (str | callable): The function to resolve.
        registry (dict): Registered modules or objects.
        decorators_list (list): List of decorators to apply.

    Returns:
        callable: Decorated function
    """        
    if isinstance(action, str) and "#" in action:
        obj_name, method = action.split("#", 1)
        obj = registry.get(obj_name)
        if obj is None:
            raise ValueError(f"Unknown object reference '{obj_name}'")
        func = getattr(obj, method)
    elif callable(action):
        func = action
    elif isinstance(action, str):
        for k, v in registry.items():
            candidate = getattr(v, action, None)
            if callable(candidate):
                func = candidate
                break
        else:
            raise ValueError(f"Invalid action string '{action}', must use 'obj#method' or be registered.")
    else:
        func = action

    # Apply decorators
    if decorators_list:
        for item in reversed(decorators_list):
            if isinstance(item, dict):
                name = item.get("name")
                args = item.get("args", [])
                fn = getattr(decorators, name, None)
                if callable(fn):
                    func = fn(*args)(func)
            elif isinstance(item, str):
                fn = getattr(decorators, item, None)
                if callable(fn):
                    func = fn(func)

    return func


def resolve_args_dnu(step: Dict[str, Any], context: Dict[str, Any]) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Resolves *args and **kwargs for a pipeline step.

    Args:
        step (dict): Step definition.
        context (dict): Shared pipeline context.

    Returns:
        tuple: Positional args list, keyword args dict.
    """
    args, kwargs = [], {}

    if "args" in step:
        val = step["args"]
        if isinstance(val, str):
            args = [resolve_arg(val, context)]
        elif isinstance(val, (list, tuple)):
            args = [resolve_arg(v, context) for v in val]
        else:
            raise TypeError(f"Invalid type for 'args': {type(val).__name__}")
    elif "input" in step:
        val = step["input"]
        if isinstance(val, dict):
            args = [resolve_arg(v, context) for v in val.pop("__args__", [])]
            kwargs = {k: resolve_arg(v, context) for k, v in val.items()}
        elif isinstance(val, list):
            args = [resolve_arg(v, context) for v in val]
        else:
            args = [resolve_arg(val, context)]

    for k, v in step.items():
        if k not in {
            "name", "action", "args", "input", "publish", "when",
            "on-success", "on-error", "timeout", "skip_hooks", "func", "decorate", "trigger", "on"
        }:
            kwargs[k] = resolve_arg(v, context)

    return args, kwargs
