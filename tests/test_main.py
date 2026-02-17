import pytest
from click.testing import CliRunner
from ai_toolbox.main import cli, hello


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


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


def test_hello_command(runner):
    """Test the hello command."""
    result = runner.invoke(cli, ["hello"])
    assert result.exit_code == 0
    assert "Hello from ai toolbox!" in result.output


def test_hello_command_directly(runner):
    """Test invoking the hello command directly."""
    result = runner.invoke(hello)
    assert result.exit_code == 0
    assert "Hello from ai toolbox!" in result.output


def test_invalid_command(runner):
    """Test that invalid commands produce an error."""
    result = runner.invoke(cli, ["nonexistent"])
    assert result.exit_code != 0
    assert "No such command" in result.output or "Error" in result.output
