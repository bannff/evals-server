"""Catalog of available Strands LLMAJ evaluators.

Provides metadata for all supported evaluators without importing
the strands_evals package (lazy import in experiment_runner).
"""

from __future__ import annotations

from typing import Any


def get_available_evaluators() -> list[dict[str, Any]]:
    """Return metadata for all supported Strands evaluators."""
    return [
        {
            "name": "output",
            "class": "OutputEvaluator",
            "level": "OUTPUT_LEVEL",
            "description": "Flexible LLM-based evaluation with custom rubrics",
            "requires_rubric": True,
        },
        {
            "name": "helpfulness",
            "class": "HelpfulnessEvaluator",
            "level": "TRACE_LEVEL",
            "description": "Evaluate response helpfulness from user perspective",
            "requires_rubric": False,
        },
        {
            "name": "faithfulness",
            "class": "FaithfulnessEvaluator",
            "level": "TRACE_LEVEL",
            "description": "Assess factual accuracy and groundedness",
            "requires_rubric": False,
        },
        {
            "name": "tool_selection",
            "class": "ToolSelectionEvaluator",
            "level": "TRACE_LEVEL",
            "description": "Evaluate whether correct tools were selected",
            "requires_rubric": False,
        },
        {
            "name": "tool_parameter",
            "class": "ToolParameterEvaluator",
            "level": "TRACE_LEVEL",
            "description": "Evaluate accuracy of tool parameters",
            "requires_rubric": False,
        },
        {
            "name": "trajectory",
            "class": "TrajectoryEvaluator",
            "level": "SESSION_LEVEL",
            "description": "Assess sequence of actions and tool usage patterns",
            "requires_rubric": True,
        },
        {
            "name": "interactions",
            "class": "InteractionsEvaluator",
            "level": "SESSION_LEVEL",
            "description": "Analyze conversation patterns and interaction quality",
            "requires_rubric": False,
        },
        {
            "name": "goal_success",
            "class": "GoalSuccessRateEvaluator",
            "level": "SESSION_LEVEL",
            "description": "Determine if user goals were successfully achieved",
            "requires_rubric": False,
        },
    ]
