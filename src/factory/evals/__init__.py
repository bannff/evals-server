"""Evals brick - agent benchmarking and evaluation framework."""

from .interface import (
    EvalRunner, EvalCase, EvalResult, EvalSuite, EvalRun,
    EvalMetrics, EvalHealth, AgentConfig, ExperimentConfig,
    ExperimentReport, EvalsRuntime, get_runtime, reset_runtime,
)
from .core import (
    create_suite, get_suite, list_suites, run_suite,
    get_run, list_runs, compute_metrics,
)

__all__ = [
    "EvalRunner", "EvalCase", "EvalResult", "EvalSuite", "EvalRun",
    "EvalMetrics", "EvalHealth", "AgentConfig", "ExperimentConfig",
    "ExperimentReport", "EvalsRuntime", "get_runtime", "reset_runtime",
    "create_suite", "get_suite", "list_suites", "run_suite",
    "get_run", "list_runs", "compute_metrics",
]
