"""UI Scenario management MCP tools.

Tools for creating and managing UI exploration scenarios.
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING
import uuid

from fastmcp import FastMCP
from factory.mcp_utils.interface import deterministic, operational

if TYPE_CHECKING:
    from ..runtime.runtime import EvalsRuntime


# Module-level UI Explorer instance
_ui_explorer: Any = None


def _get_explorer() -> Any:
    """Get or create UI Explorer instance."""
    global _ui_explorer
    if _ui_explorer is None:
        from ..runtime.adapters import UIExplorerRunner
        _ui_explorer = UIExplorerRunner()
    return _ui_explorer


def register(mcp: FastMCP, get_runtime: Callable[[], "EvalsRuntime"]) -> None:
    """Register UI scenario management tools."""

    @mcp.tool()
    @deterministic
    def evals_ui_get_capabilities() -> dict[str, Any]:
        """Get UI Explorer capabilities."""
        return {
            "name": "UI Explorer",
            "description": "Agentic UI testing via Chrome DevTools MCP",
            "actions": ["click", "fill", "hover", "wait", "navigate", "press_key"],
            "assertions": ["console_clean", "network_ok", "a11y_valid", "performance_budget"],
            "reporters": ["file", "console"],
            "requires": "chrome-devtools MCP server",
        }

    @mcp.tool()
    @operational
    def evals_create_ui_scenario(
        name: str,
        route: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new UI exploration scenario."""
        from ..runtime.ui import UIScenario

        explorer = _get_explorer()
        scenario = UIScenario(
            id=str(uuid.uuid4()),
            name=name,
            route=route,
            description=description,
            tags=tags or [],
        )
        explorer.create_scenario(scenario)
        return {
            "id": scenario.id,
            "name": scenario.name,
            "route": scenario.route,
            "message": "Scenario created. Add actions and assertions next.",
        }

    @mcp.tool()
    @deterministic
    def evals_list_ui_scenarios() -> dict[str, Any]:
        """List all registered UI scenarios."""
        explorer = _get_explorer()
        scenarios = explorer.list_scenarios()
        return {"scenarios": [s.to_dict() for s in scenarios], "count": len(scenarios)}

    @mcp.tool()
    @deterministic
    def evals_get_ui_scenario(scenario_id: str) -> dict[str, Any]:
        """Get a UI scenario by ID."""
        explorer = _get_explorer()
        scenario = explorer.get_scenario(scenario_id)
        if not scenario:
            return {"error": f"Scenario not found: {scenario_id}"}
        return scenario.to_dict()
