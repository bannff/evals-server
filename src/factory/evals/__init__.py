"""Evals brick - agent benchmarking and evaluation framework.

This brick provides a unified interface for evaluating agents across
multiple backends (custom, Strands Evals SDK).
"""

from .interface import (
    create_server,
    Runtime,
    EvalRunner,
    EvalCase,
    EvalResult,
    EvalSuite,
    EvalRun,
    EvalMetrics,
    EvalHealth,
    AgentConfig,
    ExperimentConfig,
    ExperimentReport,
    get_runtime,
    reset_runtime,
)
from .core import (
    create_suite,
    get_suite,
    list_suites,
    run_suite,
    get_run,
    list_runs,
    compute_metrics,
)

__all__ = [
    "create_server",
    "Runtime",
    "EvalRunner",
    "EvalCase",
    "EvalResult",
    "EvalSuite",
    "EvalRun",
    "EvalMetrics",
    "EvalHealth",
    "AgentConfig",
    "ExperimentConfig",
    "ExperimentReport",
    "get_runtime",
    "reset_runtime",
    "create_suite",
    "get_suite",
    "list_suites",
    "run_suite",
    "get_run",
    "list_runs",
    "compute_metrics",
]
