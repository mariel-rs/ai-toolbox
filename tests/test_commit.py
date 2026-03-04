import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import subprocess
from commands.commit import commit, get_staged_diff, generate_commit_message, run_git_commit
from litellm import AuthenticationError


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

    @patch("commands.commit.subprocess.run")
    def test_raises_runtime_error_when_git_not_installed(self, mock_run):
        """Test that get_staged_diff raises RuntimeError when git is not found."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(RuntimeError) as exc_info:
            get_staged_diff()

        assert "Git is not installed" in str(exc_info.value)


class TestGenerateCommitMessage:
    """Tests for the generate_commit_message function."""

    @patch("commands.commit.completion")
    def test_returns_generated_message(self, mock_completion):
        """Test that generate_commit_message returns the LLM response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "feat(api): add new endpoint"
        mock_completion.return_value = mock_response

        messages = [{"role": "user", "content": "test prompt"}]
        result = generate_commit_message(messages)

        assert result == "feat(api): add new endpoint"
        mock_completion.assert_called_once_with(
            model="openai/gpt-4o-mini",
            messages=messages,
            temperature=0.2
        )

    @patch("commands.commit.completion")
    def test_strips_whitespace_from_response(self, mock_completion):
        """Test that generate_commit_message strips whitespace from response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "  feat: add feature  \n"
        mock_completion.return_value = mock_response

        messages = [{"role": "user", "content": "test prompt"}]
        result = generate_commit_message(messages)

        assert result == "feat: add feature"


class TestRunGitCommit:
    """Tests for the run_git_commit function."""

    @patch("commands.commit.subprocess.run")
    def test_executes_git_commit(self, mock_run):
        """Test that run_git_commit executes git commit with the message."""
        mock_run.return_value = MagicMock(stdout="[main abc123] feat: test\n")

        run_git_commit("feat: test commit")

        mock_run.assert_called_once_with(
            ["git", "commit", "-m", "feat: test commit"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch("commands.commit.subprocess.run")
    def test_raises_runtime_error_on_failure(self, mock_run):
        """Test that run_git_commit raises RuntimeError on git failure."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["git", "commit", "-m", "test"],
            stderr="error: nothing to commit"
        )

        with pytest.raises(RuntimeError) as exc_info:
            run_git_commit("test")

        assert "Git commit failed" in str(exc_info.value)


class TestCommitCommand:
    """Tests for the commit CLI command."""

    @patch("commands.commit.run_git_commit")
    @patch("commands.commit.generate_commit_message")
    @patch("commands.commit.get_staged_diff")
    def test_commit_approved(self, mock_get_diff, mock_generate, mock_run_commit, runner):
        """Test commit command when user approves the generated message."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"
        mock_generate.return_value = "feat(test): add new feature"

        result = runner.invoke(commit, input="a")

        assert result.exit_code == 0
        assert "Generating commit message, please hold..." in result.output
        assert "feat(test): add new feature" in result.output
        assert "Commit successful!" in result.output
        mock_run_commit.assert_called_once_with("feat(test): add new feature")

    @patch("commands.commit.run_git_commit")
    @patch("commands.commit.generate_commit_message")
    @patch("commands.commit.get_staged_diff")
    def test_commit_rejected(self, mock_get_diff, mock_generate, mock_run_commit, runner):
        """Test commit command when user rejects the generated message."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"
        mock_generate.return_value = "feat(test): add new feature"

        result = runner.invoke(commit, input="r")

        assert result.exit_code == 0
        assert "Aborted." in result.output
        mock_run_commit.assert_not_called()

    @patch("commands.commit.run_git_commit")
    @patch("commands.commit.generate_commit_message")
    @patch("commands.commit.get_staged_diff")
    def test_commit_adjusted_then_approved(self, mock_get_diff, mock_generate, mock_run_commit, runner):
        """Test commit command when user adjusts then approves."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"
        mock_generate.side_effect = ["feat(test): initial message", "fix(test): adjusted message"]

        result = runner.invoke(commit, input="e\nmake it a fix instead\na")

        assert result.exit_code == 0
        assert "feat(test): initial message" in result.output
        assert "fix(test): adjusted message" in result.output
        assert "Commit successful!" in result.output
        mock_run_commit.assert_called_once_with("fix(test): adjusted message")
        assert mock_generate.call_count == 2

    @patch("commands.commit.run_git_commit")
    @patch("commands.commit.generate_commit_message")
    @patch("commands.commit.get_staged_diff")
    def test_commit_adjusted_then_rejected(self, mock_get_diff, mock_generate, mock_run_commit, runner):
        """Test commit command when user adjusts then rejects."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"
        mock_generate.side_effect = ["feat(test): initial message", "fix(test): adjusted message"]

        result = runner.invoke(commit, input="e\nmake it a fix\nr")

        assert result.exit_code == 0
        assert "Aborted." in result.output
        mock_run_commit.assert_not_called()

    @patch("commands.commit.get_staged_diff")
    def test_commit_with_no_staged_changes(self, mock_get_diff, runner):
        """Test commit command when there are no staged changes."""
        mock_get_diff.return_value = ""

        result = runner.invoke(commit)

        assert result.exit_code == 0
        assert "No staged changes found" in result.output

    @patch("commands.commit.get_staged_diff")
    def test_commit_handles_runtime_error(self, mock_get_diff, runner):
        """Test commit command handles RuntimeError gracefully."""
        mock_get_diff.side_effect = RuntimeError("Not a git repository")

        result = runner.invoke(commit)

        assert "Error: Not a git repository" in result.output

    @patch("commands.commit.generate_commit_message")
    @patch("commands.commit.get_staged_diff")
    def test_commit_handles_authentication_error(self, mock_get_diff, mock_generate, runner):
        """Test commit command handles AuthenticationError gracefully."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"
        mock_generate.side_effect = AuthenticationError(
            message="Invalid API key",
            llm_provider="openai",
            model="gpt-4o-mini"
        )

        result = runner.invoke(commit)

        assert "Authentication failed" in result.output

    @patch("commands.commit.run_git_commit")
    @patch("commands.commit.generate_commit_message")
    @patch("commands.commit.get_staged_diff")
    def test_commit_handles_git_commit_failure(self, mock_get_diff, mock_generate, mock_run_commit, runner):
        """Test commit command handles git commit failure gracefully."""
        mock_get_diff.return_value = "diff --git a/file.py\n+new line"
        mock_generate.return_value = "feat: test"
        mock_run_commit.side_effect = RuntimeError("Git commit failed: nothing to commit")

        result = runner.invoke(commit, input="a")

        assert "Error: Git commit failed" in result.output
