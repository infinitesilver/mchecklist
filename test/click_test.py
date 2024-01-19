import click
from click import echo

@click.group()
def cli():
    pass

@click.command()
@click.option('--path', help='path to destination')
def path_create(path: str):
    """Creates the designated path! (Not actually, just pretends to)"""

    echo(f"{path} created.")


@click.command()
def hello():
    """Says hello"""

    echo('hello')


if __name__ == '__main__':
    cli.add_command(path_create)
    cli.add_command(hello)
    cli()