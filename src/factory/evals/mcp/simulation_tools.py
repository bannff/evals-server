"""MCP tools for ActorSimulator multi-turn conversation simulation.

Exposes the Strands ActorSimulator through the MCP interface for
running realistic multi-turn conversations against an agent.
"""
from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from fastmcp import FastMCP
from factory.mcp_utils.interface import operational

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register simulation tools."""

    @mcp.tool()
    @operational
    def evals_run_simulation(
        cases: list[dict[str, Any]],
        evaluator_names: list[str] | None = None,
        rubric: str = "",
        model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0",
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.1,
        max_turns: int = 10,
        experiment_name: str = "simulation",
    ) -> dict[str, Any]:
        """Run multi-turn simulation using ActorSimulator.

        Creates a simulated user that drives conversation with the agent,
        then evaluates the interaction with the configured evaluators.

        Args:
            cases: Test cases with 'name', 'input', and optional
                   'metadata' (include 'task_description' for goal eval).
            evaluator_names: Evaluators to use. Defaults to
                ['helpfulness', 'goal_success'].
            rubric: Custom rubric for evaluators that require one.
            model_id: Bedrock model ID for the agent under test.
            system_prompt: System prompt for the agent under test.
            temperature: Temperature for the agent.
            max_turns: Maximum conversation turns per case.
            experiment_name: Name for this simulation run.

        Returns:
            Simulation report with per-case scores and summary.
        """
        from ..runtime.ports import EvalCase, AgentConfig, ExperimentConfig

        runtime = get_runtime()
        eval_cases = [
            EvalCase(
                id=c.get("id", f"case-{i}"),
                name=c.get("name", f"case-{i}"),
                input=c.get("input", ""),
                expected=c.get("expected_output"),
                metadata=c.get("metadata", {}),
            )
            for i, c in enumerate(cases)
        ]

        config = ExperimentConfig(
            cases=eval_cases,
            evaluator_names=evaluator_names or ["helpfulness", "goal_success"],
            agent_config=AgentConfig(
                model_id=model_id,
                system_prompt=system_prompt,
                temperature=temperature,
            ),
            rubric=rubric,
            name=experiment_name,
        )

        try:
            report = runtime.run_simulation(config, max_turns)
            return {
                "name": report.experiment_name,
                "case_results": report.case_results,
                "summary": report.summary,
                "evaluators_used": report.evaluator_names,
            }
        except RuntimeError as e:
            return {"error": str(e)}
