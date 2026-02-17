import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from ai_toolbox.main import cli, hello


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_completion():
    """Mock litellm completion response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello from the AI toolbox!"
    return mock_response


def test_cli_help(runner):
    """Test that the CLI shows help text."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "AI Toolbox" in result.output
    assert "A command-line tool for AI utilities" in result.output


def test_cli_no_args(runner):
    """Test that the CLI runs without errors when no arguments are provided."""
    result = runner.invoke(cli)
    assert result.exit_code != 0


@patch("ai_toolbox.main.completion")
def test_hello_command(mock_completion_func, runner, mock_completion):
    """Test the hello command with mocked AI response."""
    mock_completion_func.return_value = mock_completion

    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert "Hello from the AI toolbox!" in result.output

    # Verify the completion was called with correct parameters
    mock_completion_func.assert_called_once()
    call_args = mock_completion_func.call_args
    assert call_args[1]["model"] == "openai/gpt-4o-mini"
    assert len(call_args[1]["messages"]) == 1
    assert call_args[1]["messages"][0]["role"] == "user"


@patch("ai_toolbox.main.completion")
def test_hello_command_directly(mock_completion_func, runner, mock_completion):
    """Test invoking the hello command directly."""
    mock_completion_func.return_value = mock_completion

    result = runner.invoke(hello)
    assert result.exit_code == 0
    assert "Hello from the AI toolbox!" in result.output


@patch("ai_toolbox.main.completion")
def test_hello_command_error_handling(mock_completion_func, runner):
    """Test that the hello command handles errors gracefully."""
    mock_completion_func.side_effect = Exception("API Error")

    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert "Error generating message" in result.output
    assert "Hello from the AI toolbox!" in result.output  # Fallback message


def test_invalid_command(runner):
    """Test that invalid commands produce an error."""
    result = runner.invoke(cli, ["nonexistent"])
    assert result.exit_code != 0
    assert "No such command" in result.output or "Error" in result.output
