"""Evals brick - agent benchmarking and evaluation framework.

This brick provides a unified interface for evaluating agents across
multiple backends (custom, Strands Evals SDK).

Usage:
    from factory.evals import create_suite, run_suite, EvalCase

    # Create a suite
    cases = [
        EvalCase(id="c1", name="Math", input={"q": "2+2"}, expected={"a": "4"}),
    ]
    suite = create_suite("math-suite", "Math Tests", cases)

    # Run against an agent
    def my_agent(input: dict) -> dict:
        return {"a": str(eval(input["q"]))}

    run = run_suite("math-suite", my_agent)
    print(f"Pass rate: {run.summary['pass_rate']}")
"""

from .interface import (
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
    EvalsRuntime,
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
    "EvalsRuntime",
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
