import click
import mchecklist
import rymapi
from rymapi import Release
from typing import Set, List
import re


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
ALL_TYPES = ["album", "ep", "mixtape"]


def _print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version 0.0.1")
    ctx.exit()


def _parse_selection(input: str, releases: List[Release] = []) -> Set[int]:
    if input == "all":
        return range(0, len(releases))
    
    if input == 0 or input == "none":
        return []

    for release in releases:
        if input.lower() == release.title.lower():
            print(releases.index(release))
            return set([releases.index(release)])

    chosen_set: Set[int] = set()
    temp = 0
    chosen = ""
    for char in input:
        if char.isnumeric():
            chosen += char
        elif char == " ":
            if temp:
                chosen_set = chosen_set.union(range(temp, int(chosen)))
                chosen = ""
                temp = 0
            else:
                chosen_set.add(int(chosen) - 1)
                chosen = ""
        elif char == "-":
            temp = int(chosen) - 1
            chosen = ""
        else:
            return None

    # Add any remaining numbers
    if chosen:
        if temp:
            chosen_set = chosen_set.union(range(temp, int(chosen)))
        else:
            chosen_set.add(int(chosen) - 1)

    return chosen_set


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
def edit(checklist_name, rename):
    """Make edits to the checklist with name CHECKLIST_NAME."""

    if not mchecklist.checklist_exists(checklist_name):
        click.echo(f"Checklist with name {checklist_name} does not exist.")
        return

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
def delete_checklist(checklist_name):
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
@click.option(
    "--type",
    type=click.Choice(["album", "ep", "mixtape"]),
    help="Only fetch releases of a certain type.",
)
@click.option(
    "--show-all", is_flag=True, type=bool, help="Show every release from the artist."
)
@click.option(
    "--add-all",
    is_flag=True,
    type=bool,
    help="Skip the selection prompt and add every release.",
)
@click.option(
    "--popularity-filter",
    type=float,
    help="Only show releases with a certain proportion of the artist's most rated release's ratings.",
)
def add(artist: str, type=None, title="", show_all=False, add_all=False, popularity_filter=0):
    """Select releases from ARTIST's discography to add."""

    releases = rymapi.get_artist_releases(artist, ALL_TYPES)

    if title:
        for release in releases:
            if title.lower() == release.title.lower():
                mchecklist.add_releases([release])
                return

    if show_all:
        filtered_releases = mchecklist.filter_releases(releases, max_len=None)
    elif popularity_filter:
        filtered_releases = mchecklist.filter_releases(releases, pop_filter=popularity_filter)
    else:
        filtered_releases = mchecklist.filter_releases(releases)

    if add_all:
        mchecklist.add_releases(filtered_releases)
        return
    
    click.echo(mchecklist.releases_to_string(filtered_releases))
    click.echo("Choose which entries to add to the playlist (e.g. 1 2 3, 1-3, or all)")
    
    while True:
        input: str = click.prompt(">>")

        selected = _parse_selection(input, filtered_releases)

        # If input is invalid, _parse_selection() returns None
        if selected == None:
            click.echo("Invald input, try again.")
            continue
        elif selected == []:
            click.echo("No releases added.")
            return
        else:
            break
    
    to_be_added = []
    for index in selected:
        to_be_added.append(filtered_releases[index])

    was_added = mchecklist.add_releases(to_be_added)

    for release_was_added in was_added:
        if release_was_added:
            break
    else:
        click.echo("Release(s) already in checklist.")
        return

    added_releases = []
    click.echo("Successfully added the following:")
    for i in range(0, len(to_be_added)):
        if was_added[i]:
            added_releases.append(to_be_added[i])

    click.echo(mchecklist.releases_to_string(added_releases, compact=True))


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


@cli.command()
def test():
    releases1 = rymapi.get_artist_releases("Sematary-1", ["album", "ep", "mixtape"])
    releases2 = rymapi.get_artist_releases("Aphex Twin", ["album", "ep", "mixtape"])
    print(mchecklist.releases_to_string(releases2 + releases1))


if __name__ == "__main__":
    cli()
