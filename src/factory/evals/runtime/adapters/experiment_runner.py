"""Strands Evals SDK experiment runner.

Bridges our EvalCase/ExperimentConfig types to the Strands Evals SDK
Case/Experiment/Evaluator types. Handles agent construction from
declarative AgentConfig.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ..ports import (
    EvalCase,
    AgentConfig,
    ExperimentConfig,
    ExperimentReport,
)

logger = logging.getLogger(__name__)


def _build_evaluators(names: list[str], rubric: str = "") -> list[Any]:
    """Build Strands evaluator instances from names."""
    from strands_evals.evaluators import (
        OutputEvaluator,
        HelpfulnessEvaluator,
        FaithfulnessEvaluator,
        TrajectoryEvaluator,
        GoalSuccessRateEvaluator,
    )

    mapping: dict[str, Any] = {
        "output": lambda: OutputEvaluator(rubric=rubric or _default_rubric()),
        "helpfulness": HelpfulnessEvaluator,
        "faithfulness": FaithfulnessEvaluator,
        "trajectory": lambda: TrajectoryEvaluator(rubric=rubric or _default_rubric()),
        "goal_success": GoalSuccessRateEvaluator,
    }

    evaluators = []
    for name in names:
        factory = mapping.get(name)
        if factory:
            evaluators.append(factory())
        else:
            logger.warning("Unknown evaluator: %s, skipping", name)
    return evaluators or [OutputEvaluator(rubric=rubric or _default_rubric())]


def _default_rubric() -> str:
    return (
        "Score 1.0 if the response is accurate, complete, and helpful. "
        "Score 0.5 if partially correct. Score 0.0 if incorrect or unhelpful."
    )


def _build_agent_fn(agent_config: AgentConfig | None):
    """Build a task function from declarative agent config."""
    from strands import Agent
    from strands_evals import Case

    config = agent_config or AgentConfig()

    def task_fn(case: Case) -> str:
        agent = Agent(
            system_prompt=config.system_prompt,
            callback_handler=None,
        )
        response = agent(case.input)
        return str(response)

    return task_fn


def _our_cases_to_strands(cases: list[EvalCase]) -> list[Any]:
    """Convert our EvalCase list to Strands Case list."""
    from strands_evals import Case

    strands_cases = []
    for c in cases:
        input_str = c.input.get("query", c.input.get("input", str(c.input)))
        expected = None
        if c.expected:
            expected = c.expected.get("output", c.expected.get("response", str(c.expected)))

        kwargs: dict[str, Any] = {
            "name": c.name or c.id,
            "input": input_str,
            "metadata": c.metadata,
        }
        if expected is not None:
            kwargs["expected_output"] = expected
        if c.expected_trajectory:
            kwargs["expected_trajectory"] = c.expected_trajectory

        strands_cases.append(Case[str, str](**kwargs))
    return strands_cases


def run_strands_experiment(config: ExperimentConfig) -> ExperimentReport:
    """Run a Strands experiment end-to-end."""
    from strands_evals import Experiment

    strands_cases = _our_cases_to_strands(config.cases)
    evaluators = _build_evaluators(config.evaluator_names, config.rubric)
    task_fn = _build_agent_fn(config.agent_config)

    experiment = Experiment[str, str](
        cases=strands_cases,
        evaluators=evaluators,
    )

    reports = experiment.run_evaluations(task_fn)
    report = reports[0] if reports else None

    case_results = []
    summary: dict[str, Any] = {}
    if report:
        for cr in report.case_results:
            case_results.append({
                "case_name": cr.case.name,
                "score": cr.evaluation_output.score,
                "passed": cr.evaluation_output.test_pass,
                "reason": cr.evaluation_output.reason,
            })
        summary = report.get_summary()

    return ExperimentReport(
        experiment_name=config.name or "experiment",
        case_results=case_results,
        summary=summary,
        evaluator_names=config.evaluator_names,
    )


def generate_strands_experiment(
    context: str,
    task_description: str,
    num_cases: int = 5,
    evaluator_name: str = "output",
) -> ExperimentConfig:
    """Generate an experiment config from context using ExperimentGenerator."""
    from strands_evals.generators import ExperimentGenerator
    from strands_evals.evaluators import OutputEvaluator, TrajectoryEvaluator

    eval_map = {
        "output": OutputEvaluator,
        "trajectory": TrajectoryEvaluator,
    }
    evaluator_cls = eval_map.get(evaluator_name, OutputEvaluator)

    generator = ExperimentGenerator[str, str](
        input_type=str,
        output_type=str,
        include_expected_output=True,
    )

    async def _generate():
        return await generator.from_context_async(
            context=context,
            task_description=task_description,
            num_cases=num_cases,
            evaluator=evaluator_cls,
        )

    experiment = asyncio.run(_generate())

    cases = []
    for i, sc in enumerate(experiment.cases):
        cases.append(EvalCase(
            id=f"gen-{i}",
            name=sc.name or f"case-{i}",
            input={"query": sc.input} if isinstance(sc.input, str) else sc.input,
            expected={"output": sc.expected_output} if sc.expected_output else None,
            metadata=sc.metadata or {},
        ))

    return ExperimentConfig(
        cases=cases,
        evaluator_names=[evaluator_name],
        name=f"generated-{task_description[:30]}",
    )
