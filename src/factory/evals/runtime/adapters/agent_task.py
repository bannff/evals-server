"""Build agent task functions for Strands experiments.

Constructs a task_fn(case) -> result callable that the Strands
Experiment runner invokes per case. Sets up in-memory telemetry
and session mapping when trace-level evaluators are requested.
"""
from __future__ import annotations

from typing import Any

from ..ports import AgentConfig
from .evaluator_factory import needs_trace

INTERACTIONS_EVALUATORS = frozenset({"interactions"})


def _needs_interactions(evaluator_names: list[str]) -> bool:
    """True if any evaluator requires interactions data."""
    return bool(set(evaluator_names) & INTERACTIONS_EVALUATORS)


def build_agent_fn(agent_config: AgentConfig | None, evaluator_names: list[str]):
    """Build a task function from declarative agent config.

    For output-only evaluators, returns a plain string.
    For interactions evaluators, returns {"interactions": [...]}.
    For trace/session evaluators, sets up StrandsEvalsTelemetry and
    returns {"output": str, "trajectory": Session}.
    """
    from strands import Agent

    config = agent_config or AgentConfig()
    trace = needs_trace(evaluator_names)
    interactions = _needs_interactions(evaluator_names)

    telemetry = None
    if trace:
        from strands_evals.telemetry import StrandsEvalsTelemetry
        telemetry = StrandsEvalsTelemetry().setup_in_memory_exporter()

    def task_fn(case) -> str | dict[str, Any]:
        if telemetry:
            telemetry.in_memory_exporter.clear()

        agent_kwargs: dict[str, Any] = {
            "system_prompt": config.system_prompt,
            "model": config.model_id,
            "callback_handler": None,
        }
        if trace:
            sid = getattr(case, "session_id", None) or case.name
            agent_kwargs["trace_attributes"] = {
                "gen_ai.conversation.id": sid,
                "session.id": sid,
            }

        agent = Agent(**agent_kwargs)
        response = agent(case.input)

        if telemetry:
            from strands_evals.mappers import StrandsInMemorySessionMapper
            spans = telemetry.in_memory_exporter.get_finished_spans()
            sid = getattr(case, "session_id", None) or case.name
            mapper = StrandsInMemorySessionMapper()
            session = mapper.map_to_session(spans, session_id=sid)

            if interactions:
                return {
                    "output": str(response),
                    "trajectory": session,
                    "interactions": _session_to_interactions(session),
                }
            return {"output": str(response), "trajectory": session}

        return str(response)

    return task_fn


def _session_to_interactions(session) -> list[dict[str, Any]]:
    """Convert a Session to interactions list for InteractionsEvaluator."""
    interactions = []
    for i, turn in enumerate(getattr(session, "turns", [])):
        interactions.append({
            "node_name": f"turn-{i}",
            "dependencies": [f"turn-{i-1}"] if i > 0 else [],
            "messages": getattr(turn, "messages", []),
        })
    return interactions or [{"node_name": "turn-0", "dependencies": [], "messages": []}]
