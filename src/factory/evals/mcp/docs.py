"""Documentation content for evals MCP resources."""

EVALS_DOCS = {
    "overview": {
        "title": "Evals Brick Overview",
        "content": """# Evals Brick

Agent benchmarking and evaluation framework for the Python Factory.

## Core Concepts

- **EvalSuite**: Collection of test cases for benchmarking
- **EvalCase**: Single test with input, expected output, and metadata
- **EvalRun**: Execution of a suite against an agent
- **EvalResult**: Outcome of a single case evaluation
- **EvalMetrics**: Aggregated statistics from a run

## Quick Start

1. Create a suite:
```
evals_create_suite(
    suite_id="my-suite",
    name="My Evaluation Suite",
    cases=[{"id": "case-1", "name": "Test 1", "input": {"query": "hello"}}]
)
```

2. List suites:
```
evals_list_suites()
```

3. Get run results:
```
evals_get_run(run_id="run-123")
```

## Adapters

- `custom` - In-memory evaluation runner (default)
- `strands` - Strands Agent SDK integration

## MCP Tools

- `evals_create_suite` - Create evaluation suite
- `evals_get_suite` - Get suite by ID
- `evals_list_suites` - List all suites
- `evals_get_run` - Get run by ID
- `evals_list_runs` - List runs
""",
    },
    "adapters": {
        "title": "Adapter Documentation",
        "content": """# Evals Adapters

The evals brick uses a polymorphic adapter pattern for different backends.

## Custom Adapter (default)

In-memory evaluation runner for testing and development.

```python
runtime = EvalsRuntime()
runner = runtime.get_runner("custom")
```

Features:
- No external dependencies
- Fast execution
- Suitable for unit tests

## Strands Adapter

Integration with Strands Agent SDK for production evaluations.

```python
runtime = EvalsRuntime()
runner = runtime.get_runner("strands")
```

Features:
- Strands agent integration
- Production-ready metrics
- Distributed execution support

## Creating Custom Adapters

Implement the `EvalRunner` protocol:

```python
class MyAdapter:
    def create_suite(self, suite: EvalSuite) -> EvalSuite: ...
    def get_suite(self, suite_id: str) -> EvalSuite | None: ...
    def list_suites(self) -> list[EvalSuite]: ...
    def run_suite(self, suite_id, agent_fn, scorer_fn) -> EvalRun: ...
    def get_run(self, run_id: str) -> EvalRun | None: ...
    def list_runs(self, suite_id: str | None) -> list[EvalRun]: ...
    def compute_metrics(self, run: EvalRun) -> EvalMetrics: ...
    def health_check(self) -> EvalHealth: ...
```
""",
    },
    "metrics": {
        "title": "Metrics Documentation",
        "content": """# Evaluation Metrics

Metrics computed from evaluation runs.

## Standard Metrics

| Metric | Description |
|--------|-------------|
| total_cases | Number of test cases |
| passed | Cases that passed |
| failed | Cases that failed |
| pass_rate | Percentage passed (0.0-1.0) |
| avg_score | Average score across cases |
| avg_duration_ms | Average execution time |

## Custom Metrics

Add custom metrics via scorer functions:

```python
def my_scorer(case: EvalCase, actual: dict) -> EvalResult:
    return EvalResult(
        case_id=case.id,
        passed=actual == case.expected,
        score=compute_similarity(actual, case.expected),
        metrics={"latency": 100, "tokens": 50}
    )
```

## Aggregation

Metrics are aggregated per run:

```python
metrics = runner.compute_metrics(run)
print(f"Pass rate: {metrics.pass_rate:.2%}")
print(f"Custom: {metrics.custom_metrics}")
```
""",
    },
}
