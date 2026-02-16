from typing import Any, Callable, TypeVar
from functools import wraps

F = TypeVar("F", bound=Callable[..., Any])

def deterministic(func: F) -> F:
    """Mark a tool as deterministic (safe, no side effects)."""
    setattr(func, "_mcp_category", "deterministic")
    return func

def operational(func: F) -> F:
    """Mark a tool as operational (stateful, idempotent)."""
    setattr(func, "_mcp_category", "operational")
    return func

def authoring(func: F) -> F:
    """Mark a tool as authoring (security-sensitive, configuration)."""
    setattr(func, "_mcp_category", "authoring")
    return func
