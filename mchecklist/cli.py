import click
import mchecklist
import re


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def _print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version 0.0.1")
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
def cli():
    pass


@cli.command()
@click.option("--name", type=str, help="Set the checklist's name.")
def create(name):
    """Create a new checklist."""

    if not name:
        filename = mchecklist.init_database()
    else:
        sanitized_name = re.sub(r'[^\w_. -]', '_', name).lower().strip()
        filename = mchecklist.init_database(sanitized_name)
    
    if not filename:
        click.echo(
            "A checklist already exists with that name. Use the edit command to rename an already existing checklist."
        )
    else:
        click.echo(f"{filename} created.")


@cli.command()
@click.argument("checklist name", type=str)
@click.option("--name", type=str, help="Change the name of the checklist")
def edit(checklist_name, name):
    if name:
        mchecklist.rename(checklist_name)


@cli.command()
@click.argument("artist", type=str)
@click.option("--title", type=str, help="Add only a specific release from the artist.")
def add(artist: str):
    """Add ARTIST to the checklist."""


@cli.command()
@click.argument("release", nargs=-1)
@click.option(
    "--artist", type=str, help="Specify an artist other than the currently focused one"
)
def check(release, artist: str):
    """Mark RELEASE as listened to."""


@cli.command()
def next():
    """Focus on a new artist."""


@click.command()
@click.argument("artist", type=str)
def fetch(artist: str):
    """Switch the focus to ARTIST."""


@cli.command()
@click.argument("artist", type=str)
def focus(artist: str):
    """Switch the focus to ARTIST."""


@cli.command()
@click.argument("artist", type=str)
def remove_artist(artist: str):
    """Remove ARTIST from the checklist entirely."""


@cli.command()
@click.argument("release", type=str)
@click.option(
    "--artist", type=str, help="Specify an artist other than the currently focused one."
)
def remove_release(release: str, artist: str):
    """Remove RELEASE from the checklist entirely."""


if __name__ == "__main__":
    cli()
