"""
controllers.py

Provides centralized logic for evaluating execution controllers like:
- timeout resolution from global and step level
"""

from typing import Optional, Union


def get_effective_timeout(global_timeout: Optional[Union[int, float]],
                          step_timeout: Optional[Union[int, float, bool]]) -> Optional[int]:
    """
    Resolve the effective timeout for a step, considering overrides.

    Logic:
    - If step_timeout is False, disable timeout.
    - If step_timeout is set, use it.
    - Otherwise, fall back to global_timeout.

    Args:
        global_timeout (int|float|None): Default timeout.
        step_timeout (int|float|None|False): Step-level override.

    Returns:
        int or None: Timeout in seconds, or None for no timeout.
    """
    if step_timeout is False:
        return None
    if step_timeout is not None:
        return step_timeout
    return global_timeout
