"""
io_utils.py

Provides utilities to:
- Load pipeline steps from YAML, JSON, or Python lists
- Save and restore executor state using pickle
"""

import json
import yaml
import pickle
from typing import Union, List, Dict, Any


def load_steps_from_source(steps: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Load pipeline steps from file or list.

    Args:
        steps (str or list): File path (YAML/JSON) or list of step dicts

    Returns:
        list: Parsed step dictionaries
    """
    if isinstance(steps, list):
        return steps
    if isinstance(steps, str):
        with open(steps, 'r') as f:
            content = f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return yaml.safe_load(content)
    raise ValueError("Steps must be a list of dicts or a file path")


def save_executor_state(executor: Any, path: str) -> None:
    """
    Save executor object to disk using pickle.

    Args:
        executor (PipelineExecutor): The executor to save.
        path (str): Destination file path.
    """
    with open(path, 'wb') as f:
        pickle.dump(executor, f)


def load_executor_state(path: str) -> Any:
    """
    Load previously saved executor object.

    Args:
        path (str): Path to pickle file.

    Returns:
        PipelineExecutor
    """
    with open(path, 'rb') as f:
        return pickle.load(f)
