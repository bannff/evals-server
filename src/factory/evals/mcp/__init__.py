"""MCP primitives for evals module.

This package contains:
- deterministic.py: Read-only query tools (contract tools)
- operational.py: Stateful eval operations
- experiment_tools.py: Strands experiment management tools
- resources.py: Static/queryable data (schemas, docs, runs)
- prompts.py: Guided workflows for common tasks
- docs.py: Documentation content
- templates.py: Prompt templates
- ui_explorer_tools.py: UI exploration via Chrome DevTools
"""

from . import (
    deterministic,
    operational,
    experiment_tools,
    resources,
    prompts,
    ui_explorer_tools,
)

__all__ = [
    "deterministic",
    "operational",
    "experiment_tools",
    "resources",
    "prompts",
    "ui_explorer_tools",
]
