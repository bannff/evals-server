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
        key = f"{backend}:{hash(frozenset(kwargs.items()))}"
        if key not in self._runners:
            self._runners[key] = self._create_runner(backend, **kwargs)
        return self._runners[key]

    def _create_runner(self, backend: str, **kwargs: Any) -> EvalRunner:
        if backend == "custom":
            from .adapters.custom_adapter import CustomEvalRunner
            return CustomEvalRunner(**kwargs)
        elif backend == "strands":
            from .adapters.strands_adapter import StrandsEvalRunner
            return StrandsEvalRunner(**kwargs)
        raise ValueError(f"Unknown evals backend: {backend}. Available: {self.available_backends()}")

    def get_strands_runner(self):
        from .adapters.strands_adapter import StrandsEvalRunner
        runner = self.get_runner("strands")
        assert isinstance(runner, StrandsEvalRunner)
        return runner

    def run_experiment(self, config: ExperimentConfig) -> ExperimentReport:
        return self.get_strands_runner().run_experiment(config)

    def generate_experiment(self, context: str, task_description: str,
                            num_cases: int = 5, evaluator_name: str = "output") -> ExperimentConfig:
        return self.get_strands_runner().generate_experiment(context, task_description, num_cases, evaluator_name)

    def run_simulation(self, config: ExperimentConfig, max_turns: int = 10) -> ExperimentReport:
        return self.get_strands_runner().run_simulation(config, max_turns)

    def save_experiment(self, config: ExperimentConfig, filename: str) -> dict:
        return self.get_strands_runner().save_experiment(config, filename)

    def load_experiment(self, filename: str) -> ExperimentConfig:
        return self.get_strands_runner().load_experiment(filename)

    def list_saved_experiments(self) -> list[dict]:
        return self.get_strands_runner().list_saved_experiments()

    def list_evaluators(self) -> list[dict[str, Any]]:
        from .adapters.strands_adapter import get_available_evaluators
        return get_available_evaluators()

    def evaluate_output(self, input_text: str, output_text: str,
                        evaluator_name: str = "output", rubric: str = "",
                        expected_output: str | None = None) -> dict[str, Any]:
        from .adapters.evaluator_adapter import evaluate_output
        return evaluate_output(input_text, output_text, evaluator_name, rubric, expected_output)

    def evaluate_output_multi(self, input_text: str, output_text: str,
                              evaluator_names: list[str], rubric: str = "",
                              expected_output: str | None = None) -> dict[str, Any]:
        from .adapters.evaluator_adapter import evaluate_output_multi
        return evaluate_output_multi(input_text, output_text, evaluator_names, rubric, expected_output)

    def create_sop_session(self, agent_description: str,
                           agent_tools: list[str] | None = None,
                           evaluation_goals: str = "") -> dict[str, Any]:
        from .adapters.sop_adapter import create_sop_session
        return create_sop_session(agent_description, agent_tools, evaluation_goals)

    def generate_sop_test_data(self, session_id: str, num_cases: int = 10,
                               evaluator_name: str = "output") -> dict[str, Any]:
        from .adapters.sop_adapter import generate_sop_test_data
        return generate_sop_test_data(session_id, num_cases, evaluator_name)

    def run_sop_evaluation(self, session_id: str, **kwargs: Any) -> dict[str, Any]:
        from .adapters.sop_adapter import run_sop_evaluation
        return run_sop_evaluation(session_id, **kwargs)

    def generate_sop_report(self, session_id: str) -> dict[str, Any]:
        from .adapters.sop_adapter import generate_sop_report
        return generate_sop_report(session_id)

    def get_sop_session(self, session_id: str) -> dict[str, Any]:
        from .adapters.sop_adapter import get_sop_session
        return get_sop_session(session_id)

    def list_sop_sessions(self) -> list[dict[str, Any]]:
        from .adapters.sop_adapter import list_sop_sessions
        return list_sop_sessions()

    def health_check(self) -> dict[str, EvalHealth]:
        return {name: runner.health_check() for name, runner in self._runners.items()}

    @staticmethod
    def available_backends() -> list[str]:
        return ["custom", "strands"]


_runtime: EvalsRuntime | None = None


def get_runtime() -> EvalsRuntime:
    global _runtime
    if _runtime is None:
        _runtime = EvalsRuntime()
    return _runtime


def reset_runtime() -> None:
    global _runtime
    _runtime = None
