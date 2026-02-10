"""UI Explorer execution MCP tools.

Tools for adding actions/assertions and running UI explorations.
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from fastmcp import FastMCP
from factory.mcp_utils.interface import deterministic, operational

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime

from .ui_scenario_tools import _get_explorer


def register(mcp: FastMCP, get_runtime: Callable[[], "EvalsRuntime"]) -> None:
    """Register UI Explorer execution tools."""

    @mcp.tool()
    @operational
    def evals_add_scenario_action(
        scenario_id: str,
        action_type: str,
        target: str | None = None,
        value: str | None = None,
        timeout_ms: int = 5000,
    ) -> dict[str, Any]:
        """Add an action to a UI scenario.

        Args:
            scenario_id: ID of the scenario
            action_type: click, fill, hover, wait, navigate, press_key
            target: Target element (uid from snapshot)
            value: Value for fill/navigate actions
            timeout_ms: Action timeout
        """
        from ..runtime.ui import Click, Fill, Hover, WaitFor, Navigate, PressKey

        explorer = _get_explorer()
        scenario = explorer.get_scenario(scenario_id)
        if not scenario:
            return {"error": f"Scenario not found: {scenario_id}"}

        action_map = {
            "click": lambda: Click(target=target or "", timeout_ms=timeout_ms),
            "fill": lambda: Fill(target=target or "", value=value or "", timeout_ms=timeout_ms),
            "hover": lambda: Hover(target=target or "", timeout_ms=timeout_ms),
            "wait": lambda: WaitFor(text=value, timeout_ms=timeout_ms),
            "navigate": lambda: Navigate(url=value, timeout_ms=timeout_ms),
            "press_key": lambda: PressKey(key=value or "Enter", timeout_ms=timeout_ms),
        }

        if action_type not in action_map:
            return {"error": f"Unknown action type: {action_type}"}

        action = action_map[action_type]()
        scenario.actions.append(action)
        return {"scenario_id": scenario_id, "action_added": action.to_dict()}

    @mcp.tool()
    @operational
    def evals_add_scenario_assertion(
        scenario_id: str,
        assertion_type: str,
        max_errors: int = 0,
        ignore_patterns: list[str] | None = None,
        allowed_failures: list[str] | None = None,
        required_landmarks: list[str] | None = None,
        lcp_ms: int = 2500,
        fid_ms: int = 100,
        cls: float = 0.1,
    ) -> dict[str, Any]:
        """Add an assertion to a UI scenario.

        Args:
            scenario_id: ID of the scenario
            assertion_type: console_clean, network_ok, a11y_valid, performance_budget
        """
        from ..runtime.ui import ConsoleClean, NetworkOK, A11yValid, PerformanceBudget

        explorer = _get_explorer()
        scenario = explorer.get_scenario(scenario_id)
        if not scenario:
            return {"error": f"Scenario not found: {scenario_id}"}

        assertion_map = {
            "console_clean": lambda: ConsoleClean(
                max_errors=max_errors, ignore_patterns=ignore_patterns or []
            ),
            "network_ok": lambda: NetworkOK(allowed_failures=allowed_failures or []),
            "a11y_valid": lambda: A11yValid(required_landmarks=required_landmarks or []),
            "performance_budget": lambda: PerformanceBudget(
                lcp_ms=lcp_ms, fid_ms=fid_ms, cls=cls
            ),
        }

        if assertion_type not in assertion_map:
            return {"error": f"Unknown assertion type: {assertion_type}"}

        assertion = assertion_map[assertion_type]()
        scenario.assertions.append(assertion)
        return {"scenario_id": scenario_id, "assertion_added": assertion.to_dict()}

    @mcp.tool()
    @operational
    def evals_run_ui_exploration(
        scenario_id: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Process UI exploration results and run assertions.

        Call AFTER using Chrome DevTools MCP to collect context.

        Args:
            scenario_id: ID of the scenario
            context: Data from Chrome DevTools (console_messages, network_requests, snapshot)
        """
        explorer = _get_explorer()
        try:
            run = explorer.run_scenario(scenario_id, context)
            findings = explorer.get_findings(run.id)
            return {
                "run_id": run.id,
                "status": run.status,
                "summary": run.summary,
                "findings": [f.to_dict() for f in findings],
            }
        except ValueError as e:
            return {"error": str(e)}

    @mcp.tool()
    @deterministic
    def evals_list_ui_findings(run_id: str) -> dict[str, Any]:
        """Get findings from a UI exploration run."""
        explorer = _get_explorer()
        findings = explorer.get_findings(run_id)
        return {"run_id": run_id, "findings": [f.to_dict() for f in findings], "count": len(findings)}
