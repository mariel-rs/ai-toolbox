# AI Toolbox Documentation

AI Toolbox is a command-line tool for AI-powered developer utilities.

## Quick Start

```bash
# Install
pip install ai-toolbox

# Set your API key
export OPENAI_API_KEY=your-api-key

# Generate a commit message
git add .
ai-toolbox commit
```

## Commands

- [commit](commit.md) - Generate AI-powered commit messages

## Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Enable debug logging |
| `--model` | `-m` | LLM model to use (default: `openai/gpt-4o-mini`) |
| `--help` | | Show help message |

## Supported Models

AI Toolbox uses [LiteLLM](https://github.com/BerriAI/litellm) for LLM integration, supporting:

- **OpenAI**: `openai/gpt-4o-mini`, `openai/gpt-4`, `openai/gpt-3.5-turbo`
- **Anthropic**: `anthropic/claude-3-sonnet`, `anthropic/claude-3-opus`
- **And many more**: See [LiteLLM supported models](https://docs.litellm.ai/docs/providers)

## Configuration

### Environment Variables

Set the API key for your chosen provider:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

### Using .env File

Create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-...
```

The tool automatically loads environment variables from `.env`.

## Architecture

```
ai-toolbox/
├── src/
│   ├── ai_toolbox/
│   │   └── main.py          # CLI entry point, logging, global options
│   └── commands/
│       └── commit.py        # Commit command implementation
├── tests/
│   ├── test_main.py         # CLI tests
│   └── test_commit.py       # Commit command tests
└── docs/
    ├── index.md             # This file
    └── commit.md            # Commit command docs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request
