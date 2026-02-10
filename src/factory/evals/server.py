"""Evals MCP server - exposes evaluation operations via FastMCP."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .runtime.runtime import get_runtime, EvalsRuntime
from .mcp import deterministic, operational, resources, prompts
from .mcp import ui_scenario_tools, ui_explorer_tools, experiment_tools


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

    return mcp


def get_capabilities() -> dict[str, Any]:
    """Return machine-readable capabilities for evals brick."""
    return {
        "name": "evals",
        "version": "2.0.0",
        "backends": ["strands", "custom", "ui_explorer"],
        "features": [
            "benchmark_suites",
            "strands_experiments",
            "llm_as_judge_evaluators",
            "experiment_generation",
            "declarative_agent_config",
        ],
    }


def health_check() -> dict[str, Any]:
    """Fast readiness probe."""
    try:
        runtime = get_runtime()
        return {"healthy": True}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


def describe_config_schema() -> dict[str, Any]:
    """Describe evals configuration schema."""
    return {
        "type": "object",
        "properties": {
            "adapter": {"type": "string", "enum": ["strands", "custom"]},
            "model_id": {"type": "string"},
            "system_prompt": {"type": "string"},
        },
    }


mcp = create_mcp_server()


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
