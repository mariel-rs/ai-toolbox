import click
import subprocess


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
        click.echo("Staged changes retrieved successfully.")
        click.echo(f"Diff length: {len(diff)} characters")
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
