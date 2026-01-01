# MyPipeline Framework

A modular, event-driven pipeline engine in Python supporting:

- Serial and parallel workflows
- Step-level decorators, timeouts, conditions, hooks
- Event-based execution (`on`, `trigger`, `publish`)
- Named pipeline templates
- Mermaid diagram visualizations
- YAML, JSON, and Python-native formats

---

## 🚀 Getting Started

```bash
pip install pyyaml
```

### Run a basic pipeline
```python
from my_pipeline.executor import PipelineExecutor
import asyncio

steps = [{"name": "hello", "action": "builtins#print", "args": ["Hello"]}]
executor = PipelineExecutor(name="demo", steps=steps)
asyncio.run(executor.execute())
```

---

## ✅ Execution Concepts

| Concept     | Description |
|-------------|-------------|
| `args`/`input` | Pass data to steps |
| `publish`   | Store result in `context['key']` |
| `on`        | Step waits for this event |
| `trigger`   | Fires event after step completes |
| `when`      | Optional condition to execute |
| `timeout`   | Per-step or global execution limit |
| `decorate`  | Apply decorators like logging/timing |
| `parallel`  | Execute step group concurrently |

---

## 📁 Directory Structure

| File                      | Description |
|---------------------------|-------------|
| `executor.py`             | Core executor |
| `staged_executor.py`      | Event-based variant |
| `template_executor.py`    | Template calling |
| `decorators.py`           | Decorator utilities |
| `compiler.py`             | Export pipeline to Python |
| `io_utils.py`             | Load/save pipeline definitions |
| `plugins/visualizer.py`   | Mermaid graph generation |
| `examples/`               | 20+ demo pipelines |

---

## 📄 Functional Documentation

### 1. `PipelineExecutor`

```python
PipelineExecutor(
    name="example",
    steps=[...],                 # list or YAML/JSON file path
    custom_objects={"math": ...},
    execution_controllers={
        "timeout": 5,
        "before": before_hook,
        "after": after_hook,
        "log": my_logger,
        "debug": True
    }
)
```

---

## 📚 Pipeline Format Skeletons

### ✅ Python Dict Skeleton
```python
[
  {
    "name": "step1",
    "action": "mod#func",
    "args": ["value"],
    "input": {
        "__args__": ["${context_var}"],
        "key": "value"
    },
    "when": "${flag} == True",
    "timeout": 3,
    "publish": "result1",
    "trigger": "event1",
    "decorate": [
        {"name": "timeit", "args": ["step1"]},
        "step_logger"
    ]
  },
  {
    "name": "step2",
    "on": "event1",
    "action": "mod#func",
    "args": ["${result1}"]
  }
]
```

---

### ✅ YAML Skeleton
```yaml
- name: step1
  action: mymod#process
  args: ["input"]
  when: "${enabled} == True"
  timeout: 2
  publish: result1
  trigger: next_event
  decorate:
    - name: timeit
      args: ["step1"]
    - step_logger

- name: step2
  on: next_event
  action: mymod#finish
  args: ["${result1}"]
```

---

### ✅ JSON Skeleton
```json
[
  {
    "name": "step1",
    "action": "mymod#prepare",
    "args": ["data"],
    "timeout": 2,
    "publish": "prepared",
    "trigger": "next"
  },
  {
    "name": "step2",
    "on": "next",
    "action": "mymod#finish",
    "args": ["${prepared}"]
  }
]
```

---

## 📦 Execution Flow

1. Load steps from file or list
2. Compile functions and arguments
3. Execute serially or in parallel
4. Use conditions and events to branch
5. Output context holds results

---

## 🛠 Plugin Support

- Visualize with `visualizer.design_view(steps)`
- Post-execution tracing with `visualizer.execution_view(logs)`

---

## 🧪 Demo Examples

Run any file from `examples/`:
```bash
python examples/01_basic_pipeline.py
```

---

## 📝 Version

- Current: **v1.0**
- Future: Step retries, DAG validation, live debugger

