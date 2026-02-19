"""Eval SOP adapter — Strands Eval SOP 4-phase workflow.

Phase 1: Plan  — analyze agent, recommend evaluators
Phase 2: Data  — generate test cases via ExperimentGenerator
Phase 3: Eval  — run Experiment.run_evaluations(task_fn)
Phase 4: Report — produce evaluation report

See: https://strandsagents.com/latest/documentation/docs/user-guide/evals-sdk/eval-sop/
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SOPState:
    """Tracks state of an Eval SOP session."""
    id: str = ""
    phase: str = "plan"
    agent_description: str = ""
    agent_tools: list[str] = field(default_factory=list)
    evaluation_goals: str = ""
    eval_plan: dict[str, Any] = field(default_factory=dict)
    test_cases: list[dict[str, Any]] = field(default_factory=list)
    eval_results: dict[str, Any] = field(default_factory=dict)
    report: str = ""


_sessions: dict[str, SOPState] = {}


def create_sop_session(
    agent_description: str,
    agent_tools: list[str] | None = None,
    evaluation_goals: str = "",
) -> dict[str, Any]:
    """Phase 1: Plan — analyze agent and create evaluation plan."""
    session_id = str(uuid.uuid4())[:8]
    tools = agent_tools or []
    recommended = _recommend_evaluators(tools, evaluation_goals)
    plan = {
        "agent_description": agent_description,
        "agent_tools": tools,
        "evaluation_goals": evaluation_goals,
        "recommended_evaluators": recommended,
        "test_categories": _infer_categories(agent_description, tools),
        "success_criteria": {"min_pass_rate": 0.75, "min_avg_score": 0.7},
    }
    state = SOPState(
        id=session_id, phase="data",
        agent_description=agent_description, agent_tools=tools,
        evaluation_goals=evaluation_goals, eval_plan=plan,
    )
    _sessions[session_id] = state
    return {"session_id": session_id, "phase": "plan",
            "next_phase": "data", "plan": plan}


def generate_sop_test_data(
    session_id: str, num_cases: int = 10,
    evaluator_name: str = "output",
) -> dict[str, Any]:
    """Phase 2: Data — generate test cases via ExperimentGenerator."""
    state = _get_session(session_id)
    if state.phase != "data":
        return {"error": f"Expected phase 'data', got '{state.phase}'"}
    try:
        from .experiment_runner import generate_strands_experiment
        config = generate_strands_experiment(
            context=state.agent_description,
            task_description=state.evaluation_goals or state.agent_description,
            num_cases=num_cases, evaluator_name=evaluator_name,
        )
        cases = [{"id": c.id, "name": c.name, "input": c.input,
                  "expected_output": c.expected, "metadata": c.metadata}
                 for c in config.cases]
    except Exception as e:
        logger.warning("ExperimentGenerator failed: %s", e)
        cases = _fallback_cases(state, num_cases)
    state.test_cases = cases
    state.phase = "eval"
    return {"session_id": session_id, "phase": "data",
            "next_phase": "eval", "cases": cases, "case_count": len(cases)}


def run_sop_evaluation(
    session_id: str,
    model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0",
    system_prompt: str = "",
    evaluator_names: list[str] | None = None,
    rubric: str = "",
) -> dict[str, Any]:
    """Phase 3: Eval — run Experiment.run_evaluations(task_fn)."""
    state = _get_session(session_id)
    if state.phase != "eval":
        return {"error": f"Expected phase 'eval', got '{state.phase}'"}
    names = evaluator_names or state.eval_plan.get(
        "recommended_evaluators", ["output"])
    from .experiment_runner import run_strands_experiment
    from ..ports import EvalCase, AgentConfig, ExperimentConfig
    eval_cases = [
        EvalCase(id=c.get("id", f"case-{i}"), name=c.get("name", f"case-{i}"),
                 input=c.get("input", ""), expected=c.get("expected_output"),
                 metadata=c.get("metadata", {}))
        for i, c in enumerate(state.test_cases)
    ]
    config = ExperimentConfig(
        cases=eval_cases, evaluator_names=names,
        agent_config=AgentConfig(
            model_id=model_id,
            system_prompt=system_prompt or state.agent_description),
        rubric=rubric, name=f"sop-{session_id}",
    )
    report = run_strands_experiment(config)
    state.eval_results = {
        "case_results": report.case_results,
        "summary": report.summary, "evaluators": report.evaluator_names,
    }
    state.phase = "report"
    return {"session_id": session_id, "phase": "eval",
            "next_phase": "report", "results": state.eval_results}


def generate_sop_report(session_id: str) -> dict[str, Any]:
    """Phase 4: Report — produce structured evaluation report."""
    state = _get_session(session_id)
    if state.phase != "report":
        return {"error": f"Expected phase 'report', got '{state.phase}'"}
    from .sop_report import build_report
    state.report = build_report(state)
    state.phase = "complete"
    return {"session_id": session_id, "phase": "report",
            "status": "complete", "report": state.report}


def get_sop_session(session_id: str) -> dict[str, Any]:
    """Get current state of an SOP session."""
    state = _get_session(session_id)
    return {"session_id": state.id, "phase": state.phase,
            "has_plan": bool(state.eval_plan),
            "case_count": len(state.test_cases),
            "has_results": bool(state.eval_results),
            "has_report": bool(state.report)}


def list_sop_sessions() -> list[dict[str, Any]]:
    """List all SOP sessions."""
    return [{"session_id": s.id, "phase": s.phase,
             "agent": s.agent_description[:80]}
            for s in _sessions.values()]


def _get_session(session_id: str) -> SOPState:
    if session_id not in _sessions:
        raise ValueError(f"SOP session not found: {session_id}")
    return _sessions[session_id]


def _recommend_evaluators(
    tools: list[str], goals: str,
) -> list[str]:
    """Recommend evaluators based on agent characteristics."""
    rec: list[str] = []
    if tools:
        rec.extend(["tool_selection", "tool_parameter"])
    gl = goals.lower()
    if "multi-turn" in gl:
        rec.extend(["helpfulness", "goal_success"])
    if "safety" in gl:
        rec.append("harmfulness")
    if "accuracy" in gl:
        rec.append("faithfulness")
    return rec or ["output", "helpfulness"]


def _infer_categories(desc: str, tools: list[str]) -> list[str]:
    cats = ["basic_functionality"]
    if tools:
        cats.append("tool_usage")
    dl = desc.lower()
    if any(w in dl for w in ("search", "query", "find")):
        cats.append("information_retrieval")
    if any(w in dl for w in ("create", "generate", "write")):
        cats.append("content_generation")
    cats.extend(["edge_cases", "error_handling"])
    return cats


def _fallback_cases(state: SOPState, n: int) -> list[dict[str, Any]]:
    cats = state.eval_plan.get("test_categories", ["general"])
    return [{"id": f"sop-case-{i}", "name": f"{cats[i % len(cats)]}-{i}",
             "input": f"Test {i}: {state.agent_description} ({cats[i % len(cats)]})",
             "metadata": {"category": cats[i % len(cats)]}}
            for i in range(n)]
