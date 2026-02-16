"""
mcp_utils - Shared MCP Utilities Brick

This is a utility library providing decorators and helpers for MCP-enabled bricks.
It is NOT an MCP-exposed brick itself (mcp_enabled: false).

Provides:
    - @deterministic: Mark tools as pure, no side effects (queries, schemas)
    - @operational: Mark tools as stateful but idempotent (CRUD operations)
    - @authoring: Mark tools as security-gated config changes

Usage:
    from factory.mcp_utils.interface import deterministic, operational, authoring

    @deterministic
    def my_query_tool():
        ...
"""
from factory.mcp_utils.interface import deterministic, operational, authoring

__all__ = ["deterministic", "operational", "authoring"]
