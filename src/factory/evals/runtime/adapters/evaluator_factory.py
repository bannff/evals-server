"""Build Strands evaluator instances from evaluator names.

Maps short names (e.g. "output", "helpfulness") to SDK evaluator
classes. Handles rubric injection for evaluators that require one.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_RUBRIC = (
    "Score 1.0 if the response is accurate, complete, and helpful. "
    "Score 0.5 if partially correct. Score 0.0 if incorrect or unhelpful."
)

OUTPUT_LEVEL_EVALUATORS = frozenset({"output"})
TRACE_LEVEL_EVALUATORS = frozenset({
    "helpfulness", "faithfulness", "coherence", "conciseness",
    "harmfulness", "response_relevance", "tool_selection", "tool_parameter",
})
SESSION_LEVEL_EVALUATORS = frozenset({
    "trajectory", "interactions", "goal_success",
})


def needs_trace(evaluator_names: list[str]) -> bool:
    """True if any evaluator requires trace/session data."""
    return bool(set(evaluator_names) - OUTPUT_LEVEL_EVALUATORS)


def build_evaluators(names: list[str], rubric: str = "") -> list[Any]:
    """Instantiate Strands evaluator objects from short names."""
    from strands_evals.evaluators import (
        OutputEvaluator, HelpfulnessEvaluator, FaithfulnessEvaluator,
        TrajectoryEvaluator, GoalSuccessRateEvaluator, InteractionsEvaluator,
        ToolSelectionAccuracyEvaluator, ToolParameterAccuracyEvaluator,
        CoherenceEvaluator, ConcisenessEvaluator,
        HarmfulnessEvaluator, ResponseRelevanceEvaluator,
    )
    r = rubric or DEFAULT_RUBRIC
    mapping: dict[str, Any] = {
        "output": lambda: OutputEvaluator(rubric=r),
        "helpfulness": HelpfulnessEvaluator,
        "faithfulness": FaithfulnessEvaluator,
        "trajectory": lambda: TrajectoryEvaluator(rubric=r),
        "goal_success": GoalSuccessRateEvaluator,
        "interactions": lambda: InteractionsEvaluator(rubric=r),
        "tool_selection": ToolSelectionAccuracyEvaluator,
        "tool_parameter": ToolParameterAccuracyEvaluator,
        "coherence": CoherenceEvaluator,
        "conciseness": ConcisenessEvaluator,
        "harmfulness": HarmfulnessEvaluator,
        "response_relevance": ResponseRelevanceEvaluator,
    }
    evals = [mapping[n]() for n in names if n in mapping]
    for n in names:
        if n not in mapping:
            logger.warning("Unknown evaluator: %s, skipping", n)
    return evals or [OutputEvaluator(rubric=r)]
