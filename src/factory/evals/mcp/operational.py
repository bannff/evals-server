"""Operational (stateful) MCP tools for evals module.

Stateful operations with @operational decorator:
- evals_create_suite
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from fastmcp import FastMCP
from factory.mcp_utils.interface import operational

from ..runtime.ports import EvalSuite, EvalCase

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


def register(
    mcp: FastMCP,
    get_runtime: Callable[[], "EvalsRuntime"],
) -> None:
    """Register operational tools."""

    @mcp.tool()
    @operational
    def evals_create_suite(
        suite_id: str,
        name: str,
        description: str = "",
        cases: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create an evaluation suite."""
        runtime = get_runtime()
        runner = runtime.get_runner()

        eval_cases = []
        for c in (cases or []):
            eval_cases.append(EvalCase(
                id=c.get("id", ""),
                name=c.get("name", ""),
                input=c.get("input", {}),
                expected=c.get("expected"),
                metadata=c.get("metadata", {}),
            ))

        suite = EvalSuite(
            id=suite_id,
            name=name,
            description=description,
            cases=eval_cases,
        )
        result = runner.create_suite(suite)
        return {
            "id": result.id,
            "name": result.name,
            "case_count": len(result.cases),
        }

    @mcp.tool()
    @operational
    def evals_delete_suite(suite_id: str) -> dict[str, Any]:
        """Delete an evaluation suite (if supported by backend)."""
        runtime = get_runtime()
        runner = runtime.get_runner()
        
        # Check if suite exists
        suite = runner.get_suite(suite_id)
        if not suite:
            return {"deleted": False, "error": f"Suite not found: {suite_id}"}
        
        # Note: Custom adapter may not support deletion
        # This is a placeholder for backends that do
        return {
            "deleted": False,
            "error": "Deletion not supported by current backend",
            "suite_id": suite_id,
        }

    @mcp.tool()
    @operational
    def evals_add_case(
        suite_id: str,
        case_id: str,
        name: str,
        input_data: dict[str, Any],
        expected: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a test case to an existing suite."""
        runtime = get_runtime()
        runner = runtime.get_runner()
        
        suite = runner.get_suite(suite_id)
        if not suite:
            return {"added": False, "error": f"Suite not found: {suite_id}"}
        
        new_case = EvalCase(
            id=case_id,
            name=name,
            input=input_data,
            expected=expected,
            metadata=metadata or {},
        )
        
        # Add case to suite
        suite.cases.append(new_case)
        
        return {
            "added": True,
            "suite_id": suite_id,
            "case_id": case_id,
            "total_cases": len(suite.cases),
        }
