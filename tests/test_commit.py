import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import subprocess
from commands.commit import commit, get_staged_diff


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestGetStagedDiff:
    """Tests for the get_staged_diff function."""

    @patch("commands.commit.subprocess.run")
    def test_returns_diff_output(self, mock_run):
        """Test that get_staged_diff returns the stdout from git diff --staged."""
        mock_run.return_value = MagicMock(stdout="diff --git a/file.py\n+new line")

        result = get_staged_diff()

        assert result == "diff --git a/file.py\n+new line"
        mock_run.assert_called_once_with(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch("commands.commit.subprocess.run")
    def test_returns_empty_string_when_no_staged_changes(self, mock_run):
        """Test that get_staged_diff returns empty string when nothing is staged."""
        mock_run.return_value = MagicMock(stdout="")

        result = get_staged_diff()

        assert result == ""

    @patch("commands.commit.subprocess.run")
    def test_raises_runtime_error_on_git_failure(self, mock_run):
        """Test that get_staged_diff raises RuntimeError when git command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128,
            cmd=["git", "diff", "--staged"],
            stderr="fatal: not a git repository"
        )

        with pytest.raises(RuntimeError) as exc_info:
            get_staged_diff()

        assert "Failed to get staged diff" in str(exc_info.value)
        assert "not a git repository" in str(exc_info.value)

    @patch("commands.commit.subprocess.run")
    def test_raises_runtime_error_when_git_not_installed(self, mock_run):
        """Test that get_staged_diff raises RuntimeError when git is not found."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(RuntimeError) as exc_info:
            get_staged_diff()

        assert "Git is not installed" in str(exc_info.value)


class TestCommitCommand:
    """Tests for the commit CLI command."""

    @patch("commands.commit.get_staged_diff")
    def test_commit_with_staged_changes(self, mock_get_diff, runner):
        """Test commit command when there are staged changes."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"

        result = runner.invoke(commit)

        assert result.exit_code == 0
        assert "Staged changes retrieved successfully" in result.output
        assert "Diff length:" in result.output

    @patch("commands.commit.get_staged_diff")
    def test_commit_with_no_staged_changes(self, mock_get_diff, runner):
        """Test commit command when there are no staged changes."""
        mock_get_diff.return_value = ""

        result = runner.invoke(commit)

        assert result.exit_code == 0
        assert "No staged changes found" in result.output
        assert "git add" in result.output

    @patch("commands.commit.get_staged_diff")
    def test_commit_handles_runtime_error(self, mock_get_diff, runner):
        """Test commit command handles RuntimeError gracefully."""
        mock_get_diff.side_effect = RuntimeError("Not a git repository")

        result = runner.invoke(commit)

        assert "Error: Not a git repository" in result.output
