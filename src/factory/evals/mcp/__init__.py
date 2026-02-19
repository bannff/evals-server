"""MCP primitives for evals module.

This package contains:
- deterministic.py: Read-only query tools (contract tools)
- operational.py: Stateful eval operations
- experiment_tools.py: Strands experiment management tools
- evaluator_tools.py: Direct evaluator invocation (no agent needed)
- sop_tools.py: Eval SOP 4-phase workflow tools
- simulation_tools.py: ActorSimulator multi-turn simulation
- serialization_tools.py: Experiment save/load
- resources.py: Static/queryable data (schemas, docs, runs)
- prompts.py: Guided workflows for common tasks
- ui_explorer_tools.py: UI exploration via Chrome DevTools
"""

from . import (
    deterministic,
    operational,
    experiment_tools,
    evaluator_tools,
    sop_tools,
    simulation_tools,
    serialization_tools,
    resources,
    prompts,
    ui_explorer_tools,
    ui_scenario_tools,
)

__all__ = [
    "deterministic",
    "operational",
    "experiment_tools",
    "evaluator_tools",
    "sop_tools",
    "simulation_tools",
    "serialization_tools",
    "resources",
    "prompts",
    "ui_explorer_tools",
    "ui_scenario_tools",
]
