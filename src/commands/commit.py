import logging
import click
import subprocess
from typing import Any
from litellm import completion
from litellm import AuthenticationError

logger = logging.getLogger(__name__)


COMMIT_MESSAGE_PROMPT = """You are an expert at writing clear, concise git commit messages following the Conventional Commits specification.

## Your Task
Analyze the provided git diff and generate a commit message.

## Conventional Commits Format
The commit message must follow this structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types (required)
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Scope (optional)
A noun describing the section of the codebase affected (e.g., api, auth, parser, cli).

### Description (required)
- Use imperative, present tense: "add" not "added" nor "adds"
- Don't capitalize the first letter
- No period at the end
- Maximum 50 characters

### Body (optional)
- Use imperative, present tense
- Explain the motivation for the change
- Contrast with previous behavior
- Wrap at 72 characters

### Footer (optional)
- Reference issues: `Closes #123`, `Fixes #456`
- Breaking changes: `BREAKING CHANGE: <description>`

## Rules
1. Analyze ALL changes in the diff holistically
2. Choose the most appropriate type based on the primary purpose of the changes
3. Keep the description concise but meaningful
4. Only include a body if the changes need additional context
5. If there are breaking changes, you MUST include a footer with `BREAKING CHANGE:`

## Examples

Simple feature:
```
feat(auth): add password reset functionality
```

Bug fix with body:
```
fix(api): handle null response from external service

The external payment API occasionally returns null instead of an error
object. This change adds null checking to prevent runtime exceptions.

Fixes #234
```

Breaking change:
```
refactor(config)!: change configuration file format to YAML

Migrate from JSON to YAML for better readability and comment support.

BREAKING CHANGE: configuration files must be converted from .json to .yaml format
```

## Git Diff to Analyze
```
{diff}
```

## Output
Respond with ONLY the commit message. No explanations, no markdown formatting, no code blocks around your response.
"""


def get_staged_diff() -> str:
    """Retrieve the contents of git diff --staged.

    Returns:
        The staged diff output as a string, or an empty string if no changes are staged.

    Raises:
        RuntimeError: If the command fails (e.g., not in a git repository).
    """
    logger.debug("Executing git diff --staged")
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug("Git diff returned %d characters", len(result.stdout))
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error("Git diff failed: %s", e.stderr)
        raise RuntimeError(f"Failed to get staged diff: {e.stderr}") from e
    except FileNotFoundError:
        logger.error("Git executable not found")
        raise RuntimeError("Git is not installed or not found in PATH")


def generate_commit_message(messages: list[dict[str, str]]) -> str:
    """Send the messages to the LLM and return the generated commit message.

    Args:
        messages: The conversation history including the prompt and any adjustments.

    Returns:
        The generated commit message.

    Raises:
        AuthenticationError: If the API key is invalid.
        Exception: If the LLM call fails.
    """
    logger.debug("Calling LLM with %d messages", len(messages))
    logger.debug("Messages: %s", messages)
    response: Any = completion(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )
    result = response.choices[0].message.content.strip()
    logger.debug("LLM response: %s", result)
    return result


def run_git_commit(message: str) -> None:
    """Execute git commit with the given message.

    Args:
        message: The commit message.

    Raises:
        RuntimeError: If the git commit fails.
    """
    logger.debug("Executing git commit with message: %s", message)
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Git commit successful")
        logger.debug("Git commit output: %s", result.stdout)
        click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Git commit failed: %s", e.stderr)
        raise RuntimeError(f"Git commit failed: {e.stderr}") from e


def prompt_user_choice() -> str:
    """Prompt the user to approve, adjust, or abort the commit message.

    Returns:
        The user's choice: 'approve', 'adjust', or 'abort'.
    """
    click.echo("[A]pprove  [E]dit  [R]eject")
    while True:
        choice = click.getchar().lower()
        logger.debug("User input: %s", choice)
        if choice == 'a':
            logger.debug("User chose to approve")
            return 'approve'
        elif choice == 'e':
            logger.debug("User chose to edit")
            return 'adjust'
        elif choice == 'r':
            logger.debug("User chose to reject")
            return 'abort'
        else:
            logger.debug("Invalid choice: %s", choice)
            click.echo("Invalid choice. Press A to approve, E to edit, or R to reject.")


@click.command()
def commit() -> None:
    """Generate a commit message based on staged changes."""
    logger.info("Starting commit command")
    try:
        diff = get_staged_diff()
        if not diff:
            logger.info("No staged changes found")
            click.echo("No staged changes found. Stage your changes with 'git add' first.")
            return

        logger.debug("Building prompt with diff of %d characters", len(diff))
        commit_prompt = COMMIT_MESSAGE_PROMPT.format(diff=diff)
        messages: list[dict[str, str]] = [{"role": "user", "content": commit_prompt}]

        click.echo("Generating commit message, please hold...")
        message = generate_commit_message(messages)
        messages.append({"role": "assistant", "content": message})
        logger.info("Initial commit message generated")

        while True:
            click.echo("\n" + "=" * 50)
            click.echo("Generated commit message:")
            click.echo("=" * 50)
            click.echo(message)
            click.echo("=" * 50 + "\n")

            choice = prompt_user_choice()

            if choice == 'approve':
                run_git_commit(message)
                click.echo("Commit successful!")
                logger.info("Commit completed successfully")
                break
            elif choice == 'adjust':
                feedback = click.prompt("Describe the changes you want")
                logger.debug("User feedback: %s", feedback)
                messages.append({"role": "user", "content": feedback})
                click.echo("Regenerating commit message, please hold...")
                message = generate_commit_message(messages)
                messages.append({"role": "assistant", "content": message})
                logger.info("Commit message regenerated after adjustment")
            else:  # abort
                logger.info("User aborted commit")
                click.echo("Aborted.")
                break

    except AuthenticationError:
        logger.error("Authentication failed")
        click.echo("Authentication failed. Check your API key.", err=True)
    except RuntimeError as e:
        logger.error("Runtime error: %s", e)
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        logger.exception("Unexpected error generating commit message")
        click.echo(f"Error generating commit message: {e}", err=True)
