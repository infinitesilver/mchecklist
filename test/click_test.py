import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('joy', required=False)
@click.option('-p', '--path', help='path to destination', show_default=True)
def path_create(path: str, joy: str):
    """Creates the designated path! (Not actually, just pretends to)"""
    click.echo(f"{path} created. {joy}")


@cli.command()
def hello():
    """Says hello"""
    click.echo('hello')


@cli.command()
def test():
    click.echo('test')


if __name__ == '__main__':
    cli()
