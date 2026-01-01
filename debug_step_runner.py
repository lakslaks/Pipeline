import asyncio
import inspect
from datetime import datetime

from .arg_resolver import resolve_args
from .controllers import get_effective_timeout
from .conditionals import evaluate_condition

async def run_serial_step(step, executor):
    name = step.get("name")
    print(f"[ENTER] run_serial_step: {name}")

    when = step.get("when")
    if when and not evaluate_condition(when, executor.context):
        print(f"[SKIP] Condition for step '{name}' evaluated to False")
        return

    func = step.get("func")
    print(f"[FUNC] {name} resolved to {func}")

    args, kwargs = resolve_args(step, executor.context)
    timeout = get_effective_timeout(executor.controllers.get("timeout"), step.get("timeout"))
    print(f"[ARGS] {args}, {kwargs} | timeout={timeout}")

    before = executor.controllers.get("before")
    after = executor.controllers.get("after")
    logger = executor.controllers.get("log")
    debug = executor.controllers.get("debug")

    if before:
        try:
            before(name, step, executor.context)
        except Exception as e:
            print(f"[WARNING] before hook failed for step '{name}': {e}")

    try:
        start_time = datetime.now()
        if timeout:
            result = await asyncio.wait_for(
                func(*args, **kwargs) if inspect.iscoroutinefunction(func)
                else asyncio.to_thread(func, *args, **kwargs),
                timeout=timeout
            )
        else:
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"[RESULT] Step '{name}' returned: {result} (in {elapsed:.2f}s)")

        if step.get("publish"):
            async with executor.context_lock:
                executor.context[step["publish"]] = result
            print(f"[PUBLISH] {step['publish']} → {result}")

        if after:
            try:
                after(name, step, executor.context, result)
            except Exception as e:
                print(f"[WARNING] after hook failed for step '{name}': {e}")

        if logger:
            logger.info(f"[{name}] Result: {result}")
        if debug:
            print(f"[DEBUG] Step {name} → {result}")

    except Exception as e:
        print(f"[ERROR] Step '{name}' failed: {e}")
        if logger:
            logger.error(f"[{name}] Error: {e}")
        if step.get("on-error"):
            await run_serial_step(executor._step_map[step["on-error"]], executor)

async def run_parallel_block(block, executor):
    join_type = block.get("join", "all")
    retry = block.get("retry", 0)
    concurrency = block.get("max_concurrency", len(block.get("steps", [])))
    steps = block.get("steps", [])
    on_error = block.get("on-error")

    print(f"[PARALLEL] Launching {len(steps)} steps with join='{join_type}'")

    sem = asyncio.Semaphore(concurrency)

    async def worker(step):
        async with sem:
            print(f"[WORKER] Launching {step.get('name')}")
            for attempt in range(retry + 1):
                try:
                    await run_serial_step(step, executor)
                    print(f"[WORKER] Completed {step.get('name')}")
                    return None
                except Exception as e:
                    print(f"[WORKER] Error in {step.get('name')}: {e}")
                    if attempt == retry:
                        return e

    tasks = [worker(step) for step in steps]
    print("[TASKS CREATED]", tasks)

    try:
        if join_type == "any":
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                if t.exception() and on_error:
                    await run_serial_step(executor._step_map[on_error], executor)
        else:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print("[PARALLEL RESULTS]", results)
            if any(isinstance(r, Exception) for r in results) and on_error:
                await run_serial_step(executor._step_map[on_error], executor)
    except Exception as e:
        raise RuntimeError(f"Parallel execution failed: {e}") from e
