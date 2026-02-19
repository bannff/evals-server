"""Deterministic (read-only) MCP tools for evals module.

Contract tools with @deterministic decorator:
- get_capabilities
- health_check
- describe_config_schema
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from fastmcp import FastMCP
from factory.mcp_utils.interface import deterministic

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register deterministic tools."""

    @mcp.tool()
    @deterministic
    def get_capabilities() -> dict[str, Any]:
        """Return machine-readable capabilities for evals brick."""
        runtime = get_runtime()
        return {
            "name": "evals",
            "version": "2.0.0",
            "backends": runtime.available_backends(),
            "features": [
                "benchmark_suites", "eval_runs", "metrics_collection",
                "result_comparison", "strands_experiments",
                "llm_as_judge_evaluators", "direct_evaluator_invocation",
                "multi_evaluator_batch", "experiment_generation",
                "declarative_agent_config", "actor_simulation",
                "experiment_serialization", "eval_sop_workflow",
            ],
            "mcp_resources": [
                "evals://schemas/*", "evals://docs/*", "evals://runs",
                "evals://metrics", "evals://evaluators", "evals://sop/sessions",
            ],
            "mcp_prompts": [
                "create_eval", "run_eval", "analyze_results",
                "compare_runs", "evaluate_output", "eval_sop",
            ],
        }

    @mcp.tool()
    @deterministic
    def health_check() -> dict[str, Any]:
        """Fast readiness probe for evals brick."""
        runtime = get_runtime()
        health = runtime.health_check()
        all_healthy = all(h.healthy for h in health.values()) if health else True
        return {
            "healthy": all_healthy,
            "runners": {
                k: {"healthy": v.healthy, "backend": v.backend}
                for k, v in health.items()
            },
        }

    @mcp.tool()
    @deterministic
    def describe_config_schema() -> dict[str, Any]:
        """Describe evals configuration schema."""
        return {
            "type": "object",
            "properties": {
                "backend": {
                    "type": "string",
                    "enum": ["custom", "strands"],
                    "description": "Evaluation backend adapter",
                },
            },
        }

    @mcp.tool()
    @deterministic
    def evals_get_suite(suite_id: str) -> dict[str, Any]:
        """Get an evaluation suite by ID."""
        runtime = get_runtime()
        runner = runtime.get_runner()
        suite = runner.get_suite(suite_id)
        if not suite:
            return {"found": False}
        return {"found": True, "id": suite.id, "name": suite.name,
                "description": suite.description, "case_count": len(suite.cases)}

    @mcp.tool()
    @deterministic
    def evals_list_suites() -> dict[str, Any]:
        """List all evaluation suites."""
        runtime = get_runtime()
        runner = runtime.get_runner()
        suites = runner.list_suites()
        return {"suites": [{"id": s.id, "name": s.name, "case_count": len(s.cases)}
                for s in suites], "count": len(suites)}

    @mcp.tool()
    @deterministic
    def evals_get_run(run_id: str) -> dict[str, Any]:
        """Get an evaluation run by ID."""
        runtime = get_runtime()
        runner = runtime.get_runner()
        run = runner.get_run(run_id)
        if not run:
            return {"found": False}
        return {"found": True, "id": run.id, "suite_id": run.suite_id,
                "status": run.status, "summary": run.summary,
                "result_count": len(run.results)}

    @mcp.tool()
    @deterministic
    def evals_list_runs(suite_id: str | None = None) -> dict[str, Any]:
        """List evaluation runs, optionally filtered by suite."""
        runtime = get_runtime()
        runner = runtime.get_runner()
        runs = runner.list_runs(suite_id)
        return {"runs": [{"id": r.id, "suite_id": r.suite_id, "status": r.status}
                for r in runs], "count": len(runs)}
