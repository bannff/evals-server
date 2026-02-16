"""MCP tools for Strands experiment management.

Exposes experiment creation, execution, generation, and evaluator listing
through the MCP interface.
"""

from __future__ import annotations

import json
from typing import Any, Callable, TYPE_CHECKING

from fastmcp import FastMCP
from factory.mcp_utils.interface import deterministic, operational

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register experiment tools."""

    @mcp.tool()
    @deterministic
    def evals_list_evaluators() -> dict[str, Any]:
        """List available Strands LLMAJ evaluators and their config."""
        runtime = get_runtime()
        evaluators = runtime.list_evaluators()
        return {"evaluators": evaluators, "count": len(evaluators)}

    @mcp.tool()
    @operational
    def evals_run_experiment(
        cases: list[dict[str, Any]],
        evaluator_names: list[str] | None = None,
        rubric: str = "",
        model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0",
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.1,
        experiment_name: str = "experiment",
    ) -> dict[str, Any]:
        """Run a Strands experiment with LLMAJ evaluators against an agent.

        Args:
            cases: List of test cases, each with 'name', 'input', and
                   optional 'expected_output' and 'metadata'.
            evaluator_names: Evaluators to use. Options: output,
                helpfulness, faithfulness, trajectory, goal_success.
                Defaults to ['output'].
            rubric: Custom rubric for output/trajectory evaluators.
            model_id: Bedrock model ID for the agent under test.
            system_prompt: System prompt for the agent under test.
            temperature: Temperature for the agent.
            experiment_name: Name for this experiment run.

        Returns:
            Experiment report with per-case scores and summary.
        """
        from ..runtime.ports import EvalCase, AgentConfig, ExperimentConfig

        runtime = get_runtime()
        eval_cases = [
            EvalCase(
                id=c.get("id", f"case-{i}"),
                name=c.get("name", f"case-{i}"),
                input=c.get("input", {}),
                expected=c.get("expected_output"),
                expected_trajectory=c.get("expected_trajectory"),
                metadata=c.get("metadata", {}),
            )
            for i, c in enumerate(cases)
        ]

        config = ExperimentConfig(
            cases=eval_cases,
            evaluator_names=evaluator_names or ["output"],
            agent_config=AgentConfig(
                model_id=model_id,
                system_prompt=system_prompt,
                temperature=temperature,
            ),
            rubric=rubric,
            name=experiment_name,
        )

        try:
            report = runtime.run_experiment(config)
            return {
                "name": report.experiment_name,
                "case_results": report.case_results,
                "summary": report.summary,
                "evaluators_used": report.evaluator_names,
            }
        except RuntimeError as e:
            return {"error": str(e)}

    @mcp.tool()
    @operational
    def evals_generate_experiment(
        context: str,
        task_description: str,
        num_cases: int = 5,
        evaluator_name: str = "output",
    ) -> dict[str, Any]:
        """Auto-generate test cases from a context description.

        Uses Strands ExperimentGenerator to create diverse test cases
        and evaluation rubrics from your agent's context.

        Args:
            context: Description of agent capabilities, tools, etc.
            task_description: What the agent does.
            num_cases: Number of test cases to generate.
            evaluator_name: Evaluator type (output or trajectory).

        Returns:
            Generated experiment config with cases ready to run.
        """
        runtime = get_runtime()
        try:
            config = runtime.generate_experiment(
                context, task_description, num_cases, evaluator_name,
            )
            return {
                "name": config.name,
                "cases": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "input": c.input,
                        "expected": c.expected,
                        "metadata": c.metadata,
                    }
                    for c in config.cases
                ],
                "evaluator_names": config.evaluator_names,
                "case_count": len(config.cases),
            }
        except RuntimeError as e:
            return {"error": str(e)}
