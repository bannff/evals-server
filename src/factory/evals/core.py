"""Core convenience functions for evals brick."""
from __future__ import annotations
from typing import Any, Callable
from .runtime.ports import EvalCase, EvalResult, EvalSuite, EvalRun, EvalMetrics
from .runtime.runtime import get_runtime

def create_suite(suite_id: str, name: str, cases: list[EvalCase] | None = None,
    description: str = "", backend: str = "custom") -> EvalSuite:
    runtime = get_runtime()
    runner = runtime.get_runner(backend)
    suite = EvalSuite(id=suite_id, name=name, description=description, cases=cases or [])
    return runner.create_suite(suite)

def get_suite(suite_id: str, backend: str = "custom") -> EvalSuite | None:
    return get_runtime().get_runner(backend).get_suite(suite_id)

def list_suites(backend: str = "custom") -> list[EvalSuite]:
    return get_runtime().get_runner(backend).list_suites()

def run_suite(suite_id: str, agent_fn: Callable[[dict[str, Any]], dict[str, Any]],
    scorer_fn: Callable[[EvalCase, dict[str, Any]], EvalResult] | None = None,
    backend: str = "custom") -> EvalRun:
    return get_runtime().get_runner(backend).run_suite(suite_id, agent_fn, scorer_fn)

def get_run(run_id: str, backend: str = "custom") -> EvalRun | None:
    return get_runtime().get_runner(backend).get_run(run_id)

def list_runs(suite_id: str | None = None, backend: str = "custom") -> list[EvalRun]:
    return get_runtime().get_runner(backend).list_runs(suite_id)

def compute_metrics(run: EvalRun, backend: str = "custom") -> EvalMetrics:
    return get_runtime().get_runner(backend).compute_metrics(run)
