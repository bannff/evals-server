"""MCP tools for Eval SOP (Standard Operating Procedure) workflow.

Exposes the 4-phase Strands Eval SOP lifecycle through MCP:
  Phase 1: evals_sop_plan — analyze agent, create evaluation plan
  Phase 2: evals_sop_generate_data — generate test cases
  Phase 3: evals_sop_run — run evaluations
  Phase 4: evals_sop_report — produce evaluation report

See: https://strandsagents.com/latest/documentation/docs/user-guide/evals-sdk/eval-sop/
"""
from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from fastmcp import FastMCP
from factory.mcp_utils.interface import deterministic, operational

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register SOP tools."""

    @mcp.tool()
    @operational
    def evals_sop_plan(
        agent_description: str,
        agent_tools: list[str] | None = None,
        evaluation_goals: str = "",
    ) -> dict[str, Any]:
        """Phase 1: Plan — analyze agent and create evaluation plan."""
        runtime = get_runtime()
        return runtime.create_sop_session(
            agent_description, agent_tools, evaluation_goals,
        )

    @mcp.tool()
    @operational
    def evals_sop_generate_data(
        session_id: str,
        num_cases: int = 10,
        evaluator_name: str = "output",
    ) -> dict[str, Any]:
        """Phase 2: Data — generate test cases for the SOP session."""
        runtime = get_runtime()
        return runtime.generate_sop_test_data(
            session_id, num_cases, evaluator_name,
        )

    @mcp.tool()
    @operational
    def evals_sop_run(
        session_id: str,
        model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0",
        system_prompt: str = "",
        evaluator_names: list[str] | None = None,
        rubric: str = "",
    ) -> dict[str, Any]:
        """Phase 3: Eval — run evaluations using the SOP plan."""
        runtime = get_runtime()
        return runtime.run_sop_evaluation(
            session_id, model_id=model_id, system_prompt=system_prompt,
            evaluator_names=evaluator_names, rubric=rubric,
        )

    @mcp.tool()
    @operational
    def evals_sop_report(session_id: str) -> dict[str, Any]:
        """Phase 4: Report — generate evaluation report."""
        runtime = get_runtime()
        return runtime.generate_sop_report(session_id)

    @mcp.tool()
    @deterministic
    def evals_sop_status(session_id: str) -> dict[str, Any]:
        """Get current state of an SOP session."""
        runtime = get_runtime()
        return runtime.get_sop_session(session_id)

    @mcp.tool()
    @deterministic
    def evals_sop_list() -> dict[str, Any]:
        """List all SOP sessions."""
        runtime = get_runtime()
        sessions = runtime.list_sop_sessions()
        return {"sessions": sessions, "count": len(sessions)}
