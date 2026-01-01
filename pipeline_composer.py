# pipeline_composer.py

import json
import yaml
import os
import pickle
from typing import List, Dict, Optional, Union
from .executor import compile_single_step


class PipelineComposer:
    def __init__(self, template_repo: str = "templates"):
        self.raw_steps: List[Dict] = []
        self.compiled_steps: List[Dict] = []
        self.template_repo = template_repo
        self.object_registry: Dict[str, Any] = {
            "re": __import__("re"),
            "builtins": __import__("builtins"),
            "os": __import__("os"),
            "operator": __import__("operator")}
        os.makedirs(self.template_repo, exist_ok=True)

    def add_step(self, step: Dict[str, Union[str, Dict]]) -> None:
        if "name" not in step and "action" in step:
            action = step["action"]
            if isinstance(action, str) and "#" in action:
                _, func_name = action.split("#")
                step["name"] = func_name
        self.raw_steps.append(step)
        self.compiled_steps.append(compile_single_step(step, self.object_registry))

    def insert_step(self, index: int, step: Dict[str, Union[str, Dict]]) -> None:
        if "name" not in step and "action" in step:
            action = step["action"]
            if isinstance(action, str) and "#" in action:
                _, func_name = action.split("#")
                step["name"] = func_name
        self.raw_steps.insert(index, step)
        self.compiled_steps.insert(index, compile_single_step(step, self.object_registry))

    def update_step(self, name: str, new_step: Dict) -> bool:
        for i, step in enumerate(self.raw_steps):
            if step.get("name") == name:
                self.raw_steps[i] = new_step
                self.compiled_steps[i] = compile_single_step(new_step, self.object_registry)
                return True
        return False

    def delete_step(self, name: str) -> bool:
        for i, step in enumerate(self.raw_steps):
            if step.get("name") == name:
                del self.raw_steps[i]
                del self.compiled_steps[i]
                return True
        return False

    def get_step(self, name: str) -> Optional[Dict]:
        return next((s for s in self.raw_steps if s.get("name") == name), None)

    def list_steps(self) -> List[str]:
        return [s.get("name") for s in self.raw_steps]

    def save_template(self, name: str) -> None:
        with open(os.path.join(self.template_repo, f"{name}.yaml"), "w") as f:
            yaml.safe_dump(self.raw_steps, f)
        with open(os.path.join(self.template_repo, f"{name}.pkl"), "wb") as f:
            pickle.dump(self.compiled_steps, f)

    def load_template(self, name: str) -> bool:
        raw_path = os.path.join(self.template_repo, f"{name}.yaml")
        compiled_path = os.path.join(self.template_repo, f"{name}.pkl")
        if os.path.exists(raw_path):
            with open(raw_path) as f:
                self.raw_steps = yaml.safe_load(f)
            self.compiled_steps = [compile_single_step(s, self.object_registry) for s in self.raw_steps]
            return True
        elif os.path.exists(compiled_path):
            with open(compiled_path, "rb") as f:
                self.compiled_steps = pickle.load(f)
            self.raw_steps = []  # Raw unavailable
            return True
        return False

    def list_templates(self) -> List[str]:
        return sorted(set(f.split(".")[0] for f in os.listdir(self.template_repo) if f.endswith((".yaml", ".pkl"))))

    def clear(self) -> None:
        self.raw_steps.clear()
        self.compiled_steps.clear()

    def to_pipeline(self, name: str = "composed"):
        from .executor import PipelineExecutor
        return PipelineExecutor(name, self.raw_steps)

    def view(self, compiled: bool = False) -> List[Dict]:
        return self.compiled_steps if compiled else self.raw_steps
