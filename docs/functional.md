# Functional Documentation: MyPipeline

## PipelineExecutor
- Manages loading, compiling, and executing a pipeline
- Supports serial and parallel execution
- Injects context and hooks
- Timeout and debug controls available

### Constructor
```python
PipelineExecutor(
    name="my_pipeline",
    steps=[...],                     # or YAML/JSON file path
    custom_objects={"math": math},
    execution_controllers={
        "timeout": 5,
        "debug": True,
        "log": logger,
        "before": before_hook,
        "after": after_hook
    }
)
```

---

## StagedExecutor
- Extends PipelineExecutor
- Allows event-driven execution (`on`, `trigger`)
- Step queue based on fired events

### Methods
```python
executor.fire("event_name")  # triggers next steps
```

---

## TemplateExecutor
- Allows calling predefined pipelines by name

### Example
```python
templates = {"greet": [...step definitions...]}
executor = TemplateExecutor(template_registry=templates)
executor.run_template("greet")
```

---

## Decorators
- `@step_logger`: logs args/result
- `@timed_step`: logs time
- `@timeit(label)`: labeled timer
- `@inject_context`: injects `context=...`
- `@memoize(key)`: stores result in `context[key]`
