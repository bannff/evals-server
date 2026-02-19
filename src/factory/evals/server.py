"""Evals MCP server - exposes evaluation operations via FastMCP.

This server registers:
- Deterministic tools (contract tools, queries)
- Operational tools (suite management)
- Resources (schemas, docs, live data)
- Prompts (guided workflows)
- UI Explorer tools (agentic UI testing)
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .runtime.runtime import get_runtime, EvalsRuntime
from .mcp import deterministic, operational, resources, prompts
from .mcp import ui_scenario_tools, ui_explorer_tools, experiment_tools
from .mcp import simulation_tools, serialization_tools
from .mcp import evaluator_tools, sop_tools
from .mcp.views import register as register_views


def create_mcp_server(runtime: EvalsRuntime | None = None) -> FastMCP:
    """Create MCP server for evals brick."""
    runtime = runtime or get_runtime()
    mcp = FastMCP("factory-evals")

    def _get_runtime() -> EvalsRuntime:
        return runtime

    deterministic.register(mcp, _get_runtime)
    operational.register(mcp, _get_runtime)
    resources.register(mcp, _get_runtime)
    prompts.register(mcp, _get_runtime)
    ui_scenario_tools.register(mcp, _get_runtime)
    ui_explorer_tools.register(mcp, _get_runtime)
    experiment_tools.register(mcp, _get_runtime)
    simulation_tools.register(mcp, _get_runtime)
    serialization_tools.register(mcp, _get_runtime)
    evaluator_tools.register(mcp, _get_runtime)
    sop_tools.register(mcp, _get_runtime)
    register_views(mcp)

    return mcp


def get_capabilities() -> dict[str, Any]:
    """Return machine-readable capabilities for evals brick."""
    return {
        "name": "evals",
        "version": "2.0.0",
        "backends": ["strands", "custom", "ui_explorer"],
        "features": [
            "benchmark_suites", "eval_runs", "metrics_collection",
            "result_comparison", "ui_exploration", "chrome_devtools_integration",
            "strands_experiments", "llm_as_judge_evaluators",
            "direct_evaluator_invocation", "multi_evaluator_batch",
            "experiment_generation", "declarative_agent_config",
            "actor_simulation", "experiment_serialization",
            "eval_sop_workflow",
        ],
    }


def health_check() -> dict[str, Any]:
    """Fast readiness probe for evals brick."""
    try:
        runtime = get_runtime()
        return {"healthy": True, "suites": len(runtime.suites)}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


def describe_config_schema() -> dict[str, Any]:
    """Describe evals configuration schema."""
    return {
        "type": "object",
        "properties": {
            "adapter": {"type": "string", "enum": ["strands", "custom"]},
            "output_dir": {"type": "string", "description": "Results output directory"},
            "model_id": {"type": "string", "description": "Bedrock model ID for agent under test"},
            "system_prompt": {"type": "string", "description": "System prompt for agent under test"},
        },
    }


mcp = create_mcp_server()


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
