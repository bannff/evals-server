"""Evals runtime factory - selects and configures eval runner adapters.

Usage:
    runtime = EvalsRuntime()
    runner = runtime.get_runner("custom")  # or "strands"
"""

from __future__ import annotations

import logging
from typing import Any

from .ports import EvalRunner, EvalHealth, ExperimentConfig, ExperimentReport

logger = logging.getLogger(__name__)


class EvalsRuntime:
    """Factory for creating eval runner adapters."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._runners: dict[str, EvalRunner] = {}
        self._suites: dict[str, Any] = {}

    def get_runner(self, backend: str = "custom", **kwargs: Any) -> EvalRunner:
        """Get or create an eval runner adapter."""
        key = f"{backend}:{hash(frozenset(kwargs.items()))}"
        if key not in self._runners:
            self._runners[key] = self._create_runner(backend, **kwargs)
        return self._runners[key]

    def _create_runner(self, backend: str, **kwargs: Any) -> EvalRunner:
        """Create an eval runner adapter."""
        if backend == "custom":
            from .adapters.custom_adapter import CustomEvalRunner
            return CustomEvalRunner(**kwargs)
        elif backend == "strands":
            from .adapters.strands_adapter import StrandsEvalRunner
            return StrandsEvalRunner(**kwargs)
        raise ValueError(
            f"Unknown evals backend: {backend}. "
            f"Available: {self.available_backends()}"
        )

    def get_strands_runner(self):
        """Get the Strands runner (typed for experiment methods)."""
        from .adapters.strands_adapter import StrandsEvalRunner
        runner = self.get_runner("strands")
        assert isinstance(runner, StrandsEvalRunner)
        return runner

    def run_experiment(self, config: ExperimentConfig) -> ExperimentReport:
        """Run a Strands experiment via the strands adapter."""
        return self.get_strands_runner().run_experiment(config)

    def generate_experiment(
        self,
        context: str,
        task_description: str,
        num_cases: int = 5,
        evaluator_name: str = "output",
    ) -> ExperimentConfig:
        """Generate experiment from context via strands adapter."""
        return self.get_strands_runner().generate_experiment(
            context, task_description, num_cases, evaluator_name,
        )

    def list_evaluators(self) -> list[dict[str, Any]]:
        """List available evaluators."""
        from .adapters.strands_adapter import get_available_evaluators
        return get_available_evaluators()

    def health_check(self) -> dict[str, EvalHealth]:
        """Check health of all active runners."""
        return {
            name: runner.health_check()
            for name, runner in self._runners.items()
        }

    @staticmethod
    def available_backends() -> list[str]:
        """List available eval backends."""
        return ["custom", "strands"]


_runtime: EvalsRuntime | None = None


def get_runtime() -> EvalsRuntime:
    """Get the global evals runtime."""
    global _runtime
    if _runtime is None:
        _runtime = EvalsRuntime()
    return _runtime


def reset_runtime() -> None:
    """Reset the global runtime (for testing)."""
    global _runtime
    _runtime = None
