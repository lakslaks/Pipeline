"""
compiler.py

Converts pipeline steps into a standalone Python script using static code generation.
Includes:
- Variable substitution
- Publishing results to context
- Optional fire() support for trigger/publish-based flow
"""

import inspect
from typing import Any, Dict, List, Set


def compile_pipeline_to_python(steps: List[Dict[str, Any]], output_path: str = "compiled_pipeline.py") -> None:
    lines: List[str] = []
    body_lines: List[str] = []
    imports: Set[str] = set()
    uses_async = False

    def resolve_var(v: Any) -> str:
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            parts = v[2:-1].split(".")
            return "ctx" + "".join([f"['{p}']" for p in parts])
        return repr(v)

    def process_step(step: Dict[str, Any]):
        nonlocal uses_async

        name = step.get("name", "unnamed_step")
        func = step.get("func")
        publish = step.get("publish")
        trigger = step.get("trigger")
        on = step.get("on")

        args, kwargs = [], []
        if "args" in step:
            val = step["args"]
            args = [resolve_var(v) for v in val] if isinstance(val, list) else [resolve_var(val)]
        elif "input" in step:
            val = step["input"]
            if isinstance(val, dict):
                args = [resolve_var(v) for v in val.pop("__args__", [])]
                kwargs = [f"{k}={resolve_var(v)}" for k, v in val.items()]
            else:
                args = [resolve_var(val)]

        for k, v in step.items():
            if k not in {"name", "action", "args", "input", "publish", "when", "timeout", "on-error", "on-success", "skip_hooks", "func", "trigger", "on"}:
                kwargs.append(f"{k}={resolve_var(v)}")

        arg_str = ", ".join(args + kwargs)
        func_name = getattr(func, "__name__", repr(func))

        try:
            mod = inspect.getmodule(func)
            if mod and mod.__name__ not in ("builtins", "__main__"):
                imports.add(f"from {mod.__name__} import {func_name}")
        except Exception:
            pass

        is_async = inspect.iscoroutinefunction(func)
        call_expr = f"await {func_name}({arg_str})" if is_async else f"{func_name}({arg_str})"
        if is_async:
            uses_async = True

        body_lines.append(f"    # Step: {name}")
        if on:
            body_lines.append(f"    # Waits on: {on}")
        body_lines.append(f"    result = {call_expr}")
        if publish:
            body_lines.append(f"    ctx['{publish}'] = result")
            body_lines.append(f"    fire('{publish}')")
        if trigger:
            body_lines.append(f"    fire('{trigger}')")
        body_lines.append("")

    for step in steps:
        process_step(step)

    if imports:
        lines.append("# Auto-imports")
        lines.extend(sorted(imports))
        lines.append("")

    if uses_async:
        lines.append("import asyncio
")

    lines.append("ctx = {}")
    lines.append("fired_events = set()
")

    lines.append("def fire(event):")
    lines.append("    print(f'[EVENT] Fired: {event}')")
    lines.append("    fired_events.add(event)
")

    if uses_async:
        lines.append("async def main():")
    else:
        lines.append("def main():")

    lines.extend(body_lines)

    if uses_async:
        lines.append("
asyncio.run(main())")
    else:
        lines.append("
main()")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"[Generated] Python pipeline written to {output_path}")
