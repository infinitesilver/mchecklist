import click
import mchecklist.mchecklist as mchecklist
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
        filename = mchecklist.init_checklist()
    else:
        filename = mchecklist.init_checklist(name)

    if not filename:
        click.echo(
            "A checklist with that name already exists. Use the edit command to rename an existing checklist."
        )
    else:
        click.echo(f"{filename} created.")


@cli.command()
@click.argument("checklist_name", type=str)
@click.option("--rename", type=str, help="Change the name of the checklist.")
def edit(ctx, checklist_name, rename):
    """Make edits to the checklist with name CHECKLIST_NAME."""

    if not mchecklist.checklist_exists(checklist_name):
        click.echo(f"Checklist with name {checklist_name} does not exist.")
        ctx.exit()

    if rename:
        new_name = mchecklist.rename_checklist(checklist_name, rename)
        if new_name:
            click.echo(f"{checklist_name} successfully renamed to {new_name}.")
        else:
            click.echo(
                f"A checklist with the name {rename} already exists, please try again."
            )

    # Checks if no options were passed
    if not rename:
        click.echo("No changes made.\nTry 'mchecklist edit -h' for help.")


@cli.command()
@click.argument("checklist_name", type=str)
def delete(checklist_name):
    """Delete a checklist with name CHECKLIST_NAME."""

    if not mchecklist.checklist_exists(checklist_name):
        click.echo(f"Checklist with name {checklist_name} does not exist.")
        return

    if click.confirm(
        "Are you sure? This will PERMANENTLY delete the checklist and all of its data.",
        abort=True,
    ):
        mchecklist.delete_checklist(checklist_name)
        click.echo(f"{checklist_name} successfully deleted.")


@cli.command()
def list():
    """Prints a list of stored checklists."""

    checklist_list = mchecklist.list_checklists()

    if checklist_list:
        for checklist_name in mchecklist.list_checklists():
            click.echo(checklist_name)
    else:
        click.echo(
            "No checklists have been created. Try 'mchecklist create' to create a checklist."
        )


@cli.command()
@click.argument("artist", type=str)
@click.option("--title", type=str, help="Add only a specific release from the artist.")
def add(artist: str):
    """Select releases from ARTIST's discography to add."""


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
