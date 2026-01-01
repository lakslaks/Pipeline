"""
conditionals.py

Handles conditional logic for pipeline steps using `when`, supporting:
- Simple string comparisons (e.g. "${x} > 5")
- Dict-based logic with operators
- Nested `and`/`or` conditions
"""

import re
from typing import Any, Dict, Union


def evaluate_condition(cond: Union[Dict[str, Any], str], context: Dict[str, Any]) -> bool:
    """
    Evaluates a condition expression using context.

    Supports:
    - Dict format: {"var": "x", "op": ">", "value": 5}
    - Nested: {"and": [...]} or {"or": [...]}
    - String: "${x} > 5"

    Args:
        cond (dict or str): Condition expression
        context (dict): Context dictionary

    Returns:
        bool: True if condition passes
    """
    if isinstance(cond, dict):
        if "and" in cond:
            return all(evaluate_condition(c, context) for c in cond["and"])
        if "or" in cond:
            return any(evaluate_condition(c, context) for c in cond["or"])
        if "var" in cond and "op" in cond and "value" in cond:
            var = context.get(cond["var"])
            op = cond["op"]
            value = _resolve_arg(cond["value"], context)
            return _compare(var, op, value)
        raise ValueError(f"Invalid condition dict: {cond}")

    elif isinstance(cond, str):
        expr = _replace_vars_with_context(cond, context)
        try:
            return eval(expr, {}, {"context": context})
        except Exception as e:
            raise ValueError(f"Failed to evaluate string condition '{cond}': {e}")

    return False


def _compare(a: Any, op: str, b: Any) -> bool:
    """Basic comparison operations."""
    return {
        "==": a == b,
        "!=": a != b,
        "<": a < b,
        ">": a > b,
        "<=": a <= b,
        ">=": a >= b,
    }[op]


def _resolve_arg(v: Any, context: Dict[str, Any]) -> Any:
    """Substitute variable from context if in ${var} format."""
    if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
        return context.get(v[2:-1])
    return v


def _replace_vars_with_context(expr: str, context: Dict[str, Any]) -> str:
    """Replaces ${var} with context['var'] in string expressions."""
    return re.sub(r"\${([a-zA-Z0-9_]+)}", r"context['\1']", expr)
