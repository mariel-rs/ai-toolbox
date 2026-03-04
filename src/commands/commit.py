import click
import subprocess


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
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get staged diff: {e.stderr}") from e
    except FileNotFoundError:
        raise RuntimeError("Git is not installed or not found in PATH")


@click.command()
def commit():
    """Generate a commit message based on staged changes."""
    try:
        diff = get_staged_diff()
        if not diff:
            click.echo("No staged changes found. Stage your changes with 'git add' first.")
            return
        commit_prompt = COMMIT_MESSAGE_PROMPT.format(diff=diff)
        click.echo("\n[commit] Commit message prompt:")
        click.echo(commit_prompt)
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
