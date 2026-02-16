# Evals Server

Standalone MCP server for agent evaluation and benchmarking, powered by the [Strands Evals SDK](https://github.com/strands-agents/strands-agents-evals).

## Features

- **12 LLMAJ Evaluators** - output, helpfulness, faithfulness, trajectory, goal_success, interactions, tool_selection, tool_parameter, coherence, conciseness, harmfulness, response_relevance
- **Experiment Management** - create, save, load, and run evaluation suites
- **ActorSimulator** - multi-turn conversation simulation with synthetic users
- **Experiment Serialization** - save/load experiment configs as JSON
- **Auto-Generated Test Cases** - generate test cases from agent context descriptions
- **UI Exploration** - browser-based evaluation with Chrome DevTools

## Quick Start

```bash
pip install -e .
evals-server
```

Or: `python -m factory.evals.server`

### MCP Config

```json
{
  "mcpServers": {
    "evals": {
      "command": "python",
      "args": ["-m", "factory.evals.server"],
      "cwd": "/path/to/evals-server",
      "env": { "AWS_REGION": "us-east-1" }
    }
  }
}
```

## Requirements

- Python 3.11+
- AWS credentials for Amazon Bedrock
- Default model: `us.anthropic.claude-sonnet-4-20250514-v1:0`
