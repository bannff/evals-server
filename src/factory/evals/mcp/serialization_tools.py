"""MCP tools for experiment serialization (save/load).

Wraps Strands SDK Experiment.to_file/from_file for persisting
and loading experiments through the MCP interface.
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
    """Register serialization tools."""

    @mcp.tool()
    @operational
    def evals_save_experiment(
        cases: list[dict[str, Any]],
        evaluator_names: list[str],
        filename: str,
        rubric: str = "",
        experiment_name: str = "",
    ) -> dict[str, Any]:
        """Save an experiment configuration to JSON.

        Uses Strands SDK Experiment.to_file() for serialization.

        Args:
            cases: Test cases with 'name', 'input', optional 'expected_output'.
            evaluator_names: Evaluators to include in the experiment.
            filename: Output filename (stored in .object_store/).
            rubric: Custom rubric for evaluators that require one.
            experiment_name: Name for the experiment.

        Returns:
            Save result with path and case count.
        """
        from ..runtime.ports import EvalCase, ExperimentConfig

        runtime = get_runtime()
        eval_cases = [
            EvalCase(
                id=c.get("id", f"case-{i}"),
                name=c.get("name", f"case-{i}"),
                input=c.get("input", {}),
                expected=c.get("expected_output"),
                metadata=c.get("metadata", {}),
            )
            for i, c in enumerate(cases)
        ]

        config = ExperimentConfig(
            cases=eval_cases,
            evaluator_names=evaluator_names,
            rubric=rubric,
            name=experiment_name or filename,
        )

        try:
            return runtime.save_experiment(config, filename)
        except RuntimeError as e:
            return {"error": str(e)}

    @mcp.tool()
    @operational
    def evals_load_experiment(filename: str) -> dict[str, Any]:
        """Load an experiment configuration from JSON.

        Uses Strands SDK Experiment.from_file() for deserialization.

        Args:
            filename: Filename to load (from .object_store/).

        Returns:
            Loaded experiment config with cases and evaluators.
        """
        runtime = get_runtime()
        try:
            config = runtime.load_experiment(filename)
            return {
                "name": config.name,
                "cases": [
                    {
                        "id": c.id, "name": c.name,
                        "input": c.input, "expected": c.expected,
                    }
                    for c in config.cases
                ],
                "evaluator_names": config.evaluator_names,
                "case_count": len(config.cases),
            }
        except (RuntimeError, FileNotFoundError) as e:
            return {"error": str(e)}

    @mcp.tool()
    @deterministic
    def evals_list_saved_experiments() -> dict[str, Any]:
        """List all saved experiment files.

        Returns:
            List of saved experiments with filenames and metadata.
        """
        runtime = get_runtime()
        experiments = runtime.list_saved_experiments()
        return {"experiments": experiments, "count": len(experiments)}
