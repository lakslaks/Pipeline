"""
staged_executor.py

Extends PipelineExecutor to support staged, event-driven execution.
Steps can declare:
- on: event(s) they listen for
- trigger: event(s) they fire after execution
- publish: context key that may also fire event (configurable)
"""

import asyncio
from collections import defaultdict
from typing import List, Dict, Any, Union
from .executor import PipelineExecutor
from .arg_resolver import resolve_args, resolve_func
from .conditionals import evaluate_condition
from .controllers import get_effective_timeout


class StagedExecutor(PipelineExecutor):
    def __init__(self, *args, publish_triggers_event=True, **kwargs):
        """
        Args:
            publish_triggers_event (bool): If True, fires event when a context key is published.
        """
        super().__init__(*args, **kwargs)
        self.publish_triggers_event = publish_triggers_event
        self.event_queue = defaultdict(list)  # event_name -> steps waiting
        self.ready_queue = []  # steps ready now
        self.events_fired = set()
        self._step_map = {}

        self._prepare_queues()

    def _prepare_queues(self):
        for step in self.compiled_steps:
            name = step.get("name")
            if name:
                self._step_map[name] = step

            if "on" in step:
                events = step["on"]
                if isinstance(events, str):
                    events = [events]
                for ev in events:
                    self.event_queue[ev].append(step)
            else:
                self.ready_queue.append(step)

    async def execute(self):
        """Executes all ready steps; later steps activated by fired events."""
        while self.ready_queue:
            step = self.ready_queue.pop(0)
            await self._run_step(step)

    async def _run_step(self, step: Dict[str, Any]):
        name = step.get("name")
        if "when" in step and not evaluate_condition(step["when"], self.context):
            return

        func = step.get("func") or resolve_func(step["action"], self.object_registry, step.get("decorate"))
        args, kwargs = resolve_args(step, self.context)
        timeout = get_effective_timeout(self.controllers.get("timeout"), step.get("timeout"))
        publish = step.get("publish")
        trigger = step.get("trigger")

        before = self.controllers.get("before")
        after = self.controllers.get("after")
        logger = self.controllers.get("log")
        debug = self.controllers.get("debug")

        if before:
            before(name, step, self.context)

        try:
            if timeout:
                result = await asyncio.wait_for(
                    func(*args, **kwargs) if asyncio.iscoroutinefunction(func)
                    else asyncio.to_thread(func, *args, **kwargs),
                    timeout=timeout
                )
            else:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            if publish:
                async with self.context_lock:
                    self.context[publish] = result
                if self.publish_triggers_event:
                    self.fire(publish)

            if trigger:
                self.fire(trigger)

            if after:
                after(name, step, self.context, result)
            if logger:
                logger.info(f"[{name}] Result: {result}")
            if debug:
                print(f"[DEBUG] {name} → {result}")

        except Exception as e:
            if logger:
                logger.error(f"[{name}] Error: {e}")
            print(f"[ERROR] Step '{name}' failed: {e}")

    def fire(self, event: str):
        """
        Fires an event, activating waiting steps.

        Args:
            event (str): The event name to fire.
        """
        if event in self.events_fired:
            return
        self.events_fired.add(event)
        next_steps = self.event_queue.pop(event, [])
        self.ready_queue.extend(next_steps)
