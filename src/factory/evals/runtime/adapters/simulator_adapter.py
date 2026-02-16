"""ActorSimulator adapter for multi-turn conversation simulation.

Wraps the Strands Evals SDK ActorSimulator to drive realistic
multi-turn conversations against an agent, then evaluate with
trace-level evaluators.
"""
from __future__ import annotations

import logging
from typing import Any

from ..ports import AgentConfig, EvalCase, ExperimentConfig, ExperimentReport

logger = logging.getLogger(__name__)


def run_simulation(config: ExperimentConfig, max_turns: int = 10) -> ExperimentReport:
    """Run multi-turn simulation using ActorSimulator.

    For each case, creates a simulator and agent, runs the
    conversation loop, then evaluates with the configured evaluators.
    """
    from strands import Agent
    from strands_evals import Case, Experiment, ActorSimulator
    from strands_evals.mappers import StrandsInMemorySessionMapper
    from strands_evals.telemetry import StrandsEvalsTelemetry

    from .evaluator_factory import build_evaluators

    agent_cfg = config.agent_config or AgentConfig()
    evaluators = build_evaluators(config.evaluator_names, config.rubric)

    telemetry = StrandsEvalsTelemetry().setup_in_memory_exporter()
    memory_exporter = telemetry.in_memory_exporter

    strands_cases = _build_cases(config.cases)

    def task_fn(case: Case) -> dict[str, Any]:
        memory_exporter.clear()
        simulator = ActorSimulator.from_case_for_user_simulator(
            case=case, max_turns=max_turns,
        )
        agent = Agent(
            system_prompt=agent_cfg.system_prompt,
            model=agent_cfg.model_id,
            callback_handler=None,
            trace_attributes={
                "gen_ai.conversation.id": case.session_id or case.name,
                "session.id": case.session_id or case.name,
            },
        )

        user_message = case.input
        agent_response = ""
        while simulator.has_next():
            agent_response = str(agent(user_message))
            user_result = simulator.act(agent_response)
            user_message = str(user_result.structured_output.message)

        spans = memory_exporter.get_finished_spans()
        mapper = StrandsInMemorySessionMapper()
        sid = case.session_id or case.name
        session = mapper.map_to_session(spans, session_id=sid)
        return {"output": agent_response, "trajectory": session}

    experiment = Experiment[str, str](cases=strands_cases, evaluators=evaluators)
    reports = experiment.run_evaluations(task_fn)

    return _build_report(config, reports)


def _build_cases(cases: list[EvalCase]) -> list:
    """Convert EvalCase list to Strands Case list."""
    from strands_evals import Case

    result = []
    for c in cases:
        raw = c.input
        input_str = raw if isinstance(raw, str) else raw.get("query", raw.get("input", str(raw)))
        kwargs: dict[str, Any] = {
            "name": c.name or c.id,
            "input": input_str,
            "metadata": c.metadata,
        }
        if c.expected:
            kwargs["expected_output"] = c.expected.get(
                "output", c.expected.get("response", str(c.expected)),
            )
        result.append(Case[str, str](**kwargs))
    return result


def _build_report(config: ExperimentConfig, reports: list) -> ExperimentReport:
    """Convert Strands reports to our ExperimentReport."""
    case_results: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}

    if reports:
        report = reports[0]
        for i, case_rec in enumerate(report.cases):
            case_results.append({
                "case_name": case_rec.get("name", f"case-{i}"),
                "score": report.scores[i] if i < len(report.scores) else 0.0,
                "passed": report.test_passes[i] if i < len(report.test_passes) else False,
                "reason": report.reasons[i] if i < len(report.reasons) else "",
            })
        passes = report.test_passes
        summary = {
            "overall_score": report.overall_score,
            "pass_rate": sum(passes) / len(passes) if passes else 0.0,
            "total_cases": len(report.cases),
            "simulation": True,
        }

    return ExperimentReport(
        experiment_name=config.name or "simulation",
        case_results=case_results,
        summary=summary,
        evaluator_names=config.evaluator_names,
    )
