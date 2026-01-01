"""
decorators.py

Common decorators to use within pipeline step functions:
- @step_logger
- @timed_step
- @inject_context
- @memoize(key)
- @timeit(label)
"""

import time
from functools import wraps


def step_logger(fn):
    """Logs step inputs and outputs."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Calling {fn.__name__} with args={args}, kwargs={kwargs}")
        result = fn(*args, **kwargs)
        print(f"[LOG] {fn.__name__} returned {result}")
        return result
    return wrapper


def timed_step(fn):
    """Measures execution time and logs it."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        print(f"[TIME] {fn.__name__} took {time.time() - start:.4f}s")
        return result
    return wrapper


def inject_context(fn):
    """Injects context into function via kwargs if expected."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        context = kwargs.pop("context", None)
        return fn(*args, **kwargs, context=context)
    return wrapper


def memoize(key):
    """
    Caches result of function in context under 'key'.

    Usage:
        @memoize("result_key")
        def expensive_op(...): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            context = kwargs.get("context")
            if context and key in context:
                return context[key]
            result = fn(*args, **kwargs)
            if context is not None:
                context[key] = result
            return result
        return wrapper
    return decorator


def timeit(label=None):
    """
    Times execution and prints with a label.

    Usage:
        @timeit("fetch_data")
        def fn(): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = fn(*args, **kwargs)
            print(f"[TIMEIT] {label or fn.__name__} took {time.time() - start:.4f}s")
            return result
        return wrapper
    return decorator
