import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def _print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 0.0.1')
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--version', is_flag=True, callback=_print_version,
              expose_value=False, is_eager=True, 
              help='Show the version and exit.')
def cli():
    pass


@cli.command()
def create():
    """Create a new checklist."""


@cli.command()
@cli.argument('artist')
def add(artist):
    """Add ARTIST to the checklist."""


@cli.command()
@cli.argument('release', prompt='Enter the index or name of the release',
              nargs=-1)
@cli.option('--artist', 
            help='Specify an artist other than the currently focused one')
def check(release, artist):
    """Mark a release as listened to."""  


@cli.command()
def next():
    """Focus on a new artist."""


@cli.command()
@cli.argument('artist')
def fetch(artist):
    """Switch the focus to ARTIST."""


@cli.command()
@cli.argument('artist')
def focus(artist):
    """Switch the focus to ARTIST."""


if __name__ == '__main__':
    cli()