"""Shared utilities for extracting tools from FastMCP server instances.

Encapsulates access to FastMCP's internal tool registry so that bridge
modules don't need to reach into private APIs directly.
"""

from __future__ import annotations

from typing import Any, Callable


def get_tool_map(mcp_server: Any) -> dict[str, Callable[..., Any]]:
    """Extract tool name→function map from a FastMCP server instance.

    This is the single place that touches FastMCP internals. If the
    internal API changes, only this function needs updating.

    Args:
        mcp_server: A FastMCP instance (or None).

    Returns:
        Dict mapping tool names to their callable functions.
    """
    if mcp_server is None:
        return {}
    tools: dict[str, Callable[..., Any]] = {}
    tool_mgr = getattr(mcp_server, "_tool_manager", None)
    if tool_mgr is None:
        return tools
    tool_registry = getattr(tool_mgr, "_tools", None)
    if tool_registry is None:
        return tools
    for name, tool in tool_registry.items():
        fn = getattr(tool, "fn", None)
        if fn is not None:
            tools[name] = fn
    return tools
