"""MCP Prompt registration for Evals brick.

Prompts provide guided workflows for common tasks:
- Creating evaluation suites
- Running evaluations
- Analyzing results
- Comparing runs
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from fastmcp import FastMCP

from .templates import PROMPT_TEMPLATES

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register all Evals prompts with the MCP server."""

    @mcp.prompt()
    def create_eval(
        name: str,
        purpose: str = "",
    ) -> str:
        """Generate guidance for creating an evaluation suite."""
        suite_id = name.lower().replace(" ", "-").replace("_", "-")
        
        return PROMPT_TEMPLATES["create_eval"]["template"].format(
            name=name,
            suite_id=suite_id,
            purpose=purpose or f"Evaluate agent performance on {name}",
        )

    @mcp.prompt()
    def run_eval(
        suite_id: str,
        backend: str = "custom",
    ) -> str:
        """Generate guidance for running evaluations."""
        return PROMPT_TEMPLATES["run_eval"]["template"].format(
            suite_id=suite_id,
            backend=backend,
        )

    @mcp.prompt()
    def analyze_results(run_id: str) -> str:
        """Generate guidance for analyzing evaluation results."""
        return PROMPT_TEMPLATES["analyze_results"]["template"].format(
            run_id=run_id,
        )

    @mcp.prompt()
    def compare_runs(
        run_a: str,
        run_b: str,
    ) -> str:
        """Generate guidance for comparing evaluation runs."""
        return PROMPT_TEMPLATES["compare_runs"]["template"].format(
            run_a=run_a,
            run_b=run_b,
        )
