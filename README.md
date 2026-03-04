# AI Toolbox

A command-line tool for AI-powered developer utilities.

## Features

- **Smart Commit Messages**: Generate conventional commit messages from staged changes using AI
- **Interactive Workflow**: Review, edit, or regenerate commit messages before committing
- **Multiple LLM Support**: Works with any model supported by LiteLLM (OpenAI, Anthropic, etc.)
- **Configurable**: Choose your preferred model via CLI options

## Installation

```bash
pip install ai-toolbox
```

## Configuration

Set your API key as an environment variable or in a `.env` file:

```bash
# For OpenAI
export OPENAI_API_KEY=your-api-key

# For Anthropic
export ANTHROPIC_API_KEY=your-api-key
```

## Usage

### Generate Commit Messages

Stage your changes and run:

```bash
ai-toolbox commit
```

The tool will:
1. Analyze your staged changes
2. Generate a conventional commit message
3. Present options to **[A]pprove**, **[E]dit**, or **[R]eject**

### CLI Options

```bash
# Use verbose logging
ai-toolbox -v commit

# Use a different model
ai-toolbox -m anthropic/claude-3-sonnet commit

# Show help
ai-toolbox --help
```

### Available Commands

| Command | Description |
|---------|-------------|
| `commit` | Generate AI-powered commit messages |
| `hello` | Print a friendly AI-generated greeting |

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mariel-rs/ai-toolbox.git
cd ai-toolbox

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Project Structure

```
ai-toolbox/
├── src/
│   ├── ai_toolbox/
│   │   └── main.py          # CLI entry point and configuration
│   └── commands/
│       └── commit.py        # Commit message generation
├── tests/
│   ├── test_main.py
│   └── test_commit.py
├── docs/
│   └── commit.md            # Commit command documentation
└── pyproject.toml
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
