# Evals Server

Standalone MCP server for agent evaluation, powered by the
[Strands Evals SDK](https://strandsagents.com/latest/documentation/docs/user-guide/evals-sdk/quickstart/).

## Install

```bash
git clone https://github.com/bannff/evals-server.git
cd evals-server
pip install -e .
```

## Setup

1. Configure AWS credentials for Bedrock (default provider):

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
# or: aws configure
```

2. Enable model access in the
   [Bedrock console](https://console.aws.amazon.com/bedrock)
   for Claude Sonnet (or your preferred model).

## Usage

Add to your IDE's `mcp.json`:

```json
{
  "mcpServers": {
    "evals": {
      "command": "evals-server",
      "args": []
    }
  }
}
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `evals_create_suite` | Create an evaluation suite with test cases |
| `evals_add_case` | Add a test case to a suite |
| `evals_list_suites` | List all suites |
| `evals_get_suite` | Get suite details |
| `evals_list_evaluators` | List available LLMAJ evaluators |
| `evals_run_experiment` | Run experiment with evaluators against an agent |
| `evals_generate_experiment` | Auto-generate test cases from context |
| `evals_list_runs` | List evaluation runs |
| `evals_get_run` | Get run details |

## Quick Example

Once connected via MCP, an agent can:

```
# 1. List available evaluators
evals_list_evaluators()

# 2. Run an experiment
evals_run_experiment(
    cases=[
        {"name": "math", "input": {"query": "What is 2+2?"}, "expected_output": {"output": "4"}},
        {"name": "capital", "input": {"query": "Capital of France?"}, "expected_output": {"output": "Paris"}}
    ],
    evaluator_names=["output", "helpfulness"],
    model_id="us.anthropic.claude-sonnet-4-20250514",
    system_prompt="You are a helpful assistant."
)

# 3. Or auto-generate test cases
evals_generate_experiment(
    context="Agent with calculator and search tools",
    task_description="Math and research assistant",
    num_cases=10
)
```
