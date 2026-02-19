"""MCP Resource registration for Evals brick.

Resources expose static/queryable data:
- Schemas for eval config and results
- Documentation on adapters and metrics
- Live evaluation runs and metrics
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable

from fastmcp import FastMCP

from .docs import EVALS_DOCS

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register all Evals resources with the MCP server."""
    from ..runtime.ports import (
        EvalCase, EvalResult, EvalSuite, EvalRun, EvalMetrics, EvalHealth,
    )

    @mcp.resource("evals://schemas/eval-config")
    def resource_eval_config_schema() -> str:
        return json.dumps({"type": "object", "properties": {
            "backend": {"type": "string", "enum": ["custom", "strands"],
                        "description": "Evaluation backend adapter"},
        }, "description": "Evals brick configuration schema"}, indent=2)

    @mcp.resource("evals://schemas/eval-result")
    def resource_eval_result_schema() -> str:
        return json.dumps({"type": "object", "properties": {
            "case_id": {"type": "string"}, "passed": {"type": "boolean"},
            "score": {"type": "number"}, "actual": {"type": "object"},
            "metrics": {"type": "object"}, "error": {"type": ["string", "null"]},
            "duration_ms": {"type": "number"},
        }, "required": ["case_id", "passed"],
        "description": "Result from a single evaluation case"}, indent=2)

    @mcp.resource("evals://docs/overview")
    def resource_docs_overview() -> str:
        return EVALS_DOCS["overview"]["content"]

    @mcp.resource("evals://docs/adapters")
    def resource_docs_adapters() -> str:
        return EVALS_DOCS["adapters"]["content"]

    @mcp.resource("evals://docs/{doc_name}")
    def resource_docs(doc_name: str) -> str:
        if doc_name in EVALS_DOCS:
            return EVALS_DOCS[doc_name]["content"]
        return f"Unknown doc: {doc_name}. Available: {list(EVALS_DOCS.keys())}"

    @mcp.resource("evals://runs")
    def resource_runs() -> str:
        runtime = get_runtime()
        runner = runtime.get_runner()
        runs = runner.list_runs()
        return json.dumps({"runs": [{"id": r.id, "suite_id": r.suite_id,
            "status": r.status, "result_count": len(r.results)}
            for r in runs[:20]], "count": len(runs)}, indent=2)

    @mcp.resource("evals://metrics")
    def resource_metrics() -> str:
        return json.dumps({"standard_metrics": [
            {"name": "total_cases", "description": "Total test cases"},
            {"name": "passed", "description": "Cases that passed"},
            {"name": "failed", "description": "Cases that failed"},
            {"name": "pass_rate", "description": "Pass percentage (0.0-1.0)"},
            {"name": "avg_score", "description": "Average score"},
            {"name": "avg_duration_ms", "description": "Average execution time"},
        ], "custom_metrics_supported": True}, indent=2)

    @mcp.resource("evals://factory")
    def resource_factory_ref() -> str:
        return json.dumps({"message": "For workspace-level operations, use foreman tools",
            "foreman_tools": ["foreman_info", "foreman_check", "foreman_guardian_check"],
            "related_bricks": {"agent": "Agents to evaluate",
                "telemetry": "Metrics collection", "workflow": "Evaluation pipelines"}}, indent=2)

    @mcp.resource("evals://evaluators")
    def resource_evaluators() -> str:
        runtime = get_runtime()
        evaluators = runtime.list_evaluators()
        return json.dumps({"evaluators": evaluators, "count": len(evaluators),
            "levels": {"OUTPUT_LEVEL": "Single response quality",
                "TRACE_LEVEL": "Turn-by-turn analysis",
                "SESSION_LEVEL": "Full conversation assessment"}}, indent=2)

    @mcp.resource("evals://sop/sessions")
    def resource_sop_sessions() -> str:
        runtime = get_runtime()
        sessions = runtime.list_sop_sessions()
        return json.dumps({"sessions": sessions, "count": len(sessions),
            "phases": ["plan", "data", "eval", "report", "complete"]}, indent=2)
