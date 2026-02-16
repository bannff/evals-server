from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

def deterministic(func: F) -> F:
    setattr(func, "_mcp_category", "deterministic")
    return func

def operational(func: F) -> F:
    setattr(func, "_mcp_category", "operational")
    return func

def authoring(func: F) -> F:
    setattr(func, "_mcp_category", "authoring")
    return func
