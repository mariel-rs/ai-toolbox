import click


@click.group()
def cli():
    """AI Toolbox - A command-line tool for AI utilities."""
    pass


@click.command()
def hello():
    """Print a greeting message."""
    click.echo("Hello from ai toolbox!")


cli.add_command(hello)


if __name__ == "__main__":
    cli()
