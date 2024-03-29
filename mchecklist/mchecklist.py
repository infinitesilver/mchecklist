import json
from pathlib import Path
from typing import Optional, Dict, List
import re
import random
import os
from rymapi import Artist, Release
import rymapi


SOURCE_DIR = Path(__file__).resolve().parent
os.chdir(SOURCE_DIR)

CHECKLIST_DIR = SOURCE_DIR.joinpath("checklists")
CONFIG_FILE = SOURCE_DIR.joinpath("config.json")

if not CONFIG_FILE.exists():
    config_json = {
        "current": "",
        "popularity_filter": 0,
        "show_ratings": False,
        "show_average": False,
    }
    with open(CONFIG_FILE, "w") as config_file:
        config_file.write(json.dumps(config_json, indent=2))

with open(CONFIG_FILE) as config_file:
    CONFIG_JSON = json.load(config_file)

CURRENT_CHECKLIST = CONFIG_JSON["current"]
CURRENT_CHECKLIST_FILE = f"checklists/{CURRENT_CHECKLIST}.json"

with open(CURRENT_CHECKLIST_FILE) as current_checklist:
    CURRENT_CHECKLIST_JSON = json.load(current_checklist)

POP_FILTER = float(CONFIG_JSON["popularity_filter"])
SHOW_RATINGS = CONFIG_JSON["show_ratings"]
SHOW_AVERAGE = CONFIG_JSON["show_average"]

CHAR_CAP = 40


def _get_checklist_path(name: str) -> Optional[Path]:
    if checklist_exists(name):
        return CHECKLIST_DIR.joinpath(f"{name}.json")
    else:
        return None


def _write_to_config(config_json) -> None:
    with open(CONFIG_FILE, "w") as config_file:
        config_file.write(json.dumps(config_json, indent=2))


def _capitalize_release_type(release_type: str) -> str:
    match (release_type):
        case ("album"):
            return "Album"
        case ("ep"):
            return "EP"
        case ("mixtape"):
            return "Mixtape"
        case ("dj-mix"):
            return "DJ Mix"
        case ("single"):
            return "Single"
        case ("compilation"):
            return "Compilation"
        case ("bootleg"):
            return "Bootleg"
        case _:
            raise ValueError("Not a valid release type")


def release_to_dict(release: Release) -> Dict:
    return {
        "artist": release.artist,
        "title": release.title,
        "link": release.link,
        "artist_link": release.artist_link,
        "year": release.year,
        "type": release.type,
    }


def dict_to_release(dict: Dict) -> Release:
    return Release(
        dict["artist"],
        dict["title"],
        dict["link"],
        dict["artist_link"],
        None,
        None,
        dict["year"],
        dict["type"],
    )


def checklist_exists(checklist_name: str) -> bool:
    return CHECKLIST_DIR.joinpath(f"{checklist_name}.json").exists()


def init_checklist(name="", genres=["All"]) -> Optional[str]:
    """Create a new JSON file for a checklist. Called by create."""

    CHECKLIST_DIR.mkdir(exist_ok=True)

    # If no name argument was passed
    if not name:
        counter = 1
        while checklist_exists(f"checklist{counter}"):
            counter += 1

        open(CHECKLIST_DIR.joinpath(f"checklist{counter}.json"), "x")
        returned_name = f"checklist{counter}"
    else:
        sanitized_name = sanitize(name)

        # If a checklist with the same name already exists
        if checklist_exists(sanitized_name):
            return None

        open(CHECKLIST_DIR.joinpath(f"{sanitized_name}.json"), "x")
        returned_name = sanitized_name

    # Edit config
    if SOURCE_DIR.joinpath("config.json").exists():
        with open(CONFIG_FILE) as config_file:
            config_json = json.load(config_file)
    else:
        config_json = {}

    config_json["current"] = returned_name

    _write_to_config(config_json)

    # Edit new checklist
    checklist_json = {"viewing": [], "to-do": [], "completed": []}

    with open(CHECKLIST_DIR.joinpath(f"{returned_name}.json"), "w") as checklist_file:
        checklist_file.write(json.dumps(checklist_json, indent=2))

    return returned_name


def rename_checklist(old_name: str, new_name: str) -> Optional[str]:
    """Renames a checklist's JSON file. Called by edit."""

    checklist_path = _get_checklist_path(old_name)

    if not checklist_path:
        return None

    sanitized_new_name = sanitize(new_name)

    if not checklist_exists(sanitized_new_name):
        checklist_path.rename(f"{sanitized_new_name}.json")

        config_json = CONFIG_JSON
        if config_json["current"] == old_name:
            config_json["current"] = sanitized_new_name
            _write_to_config(config_json)

        return sanitized_new_name
    else:
        return None


def delete_checklist(name: str) -> Optional[str]:
    """Deletes a checklist's JSON file. Called by delete."""

    checklist_path = _get_checklist_path(name)

    if checklist_path:
        checklist_path.unlink()

        config_json = CONFIG_JSON

        if config_json["current"] == name:
            config_json["current"] == ""
            _write_to_config(config_json)

        return name
    else:
        return None


def filter_releases(releases: List[Release], max_len=15, pop_filter=0):
    """Returns a new list with only the MAX_LEN releases with the highest ratings."""

    releases_copy = releases.copy()

    if pop_filter and pop_filter <= 1:
        highest_ratings_release = max(releases_copy, key=lambda x: int(x.ratings))

        bound = len(releases_copy)
        i = 0
        while i < bound:
            release = releases_copy[i]
            if int(release.ratings) < pop_filter * int(highest_ratings_release.ratings):
                releases_copy.remove(release)
                bound -= 1
            else:
                i += 1

    if not max_len == None and len(releases_copy) > max_len:
        filtered_releases: List[Release] = []
        while len(filtered_releases) < max_len:
            highest_ratings_release = max(releases_copy, key=lambda x: int(x.ratings))
            filtered_releases.append(highest_ratings_release)
            releases_copy.remove(highest_ratings_release)
    else:
        filtered_releases = releases_copy

    filtered_releases.sort(key=lambda x: int(x.year))
    filtered_releases.sort(key=lambda x: x.type)

    return filtered_releases


def releases_to_string(
    releases: List[Release],
    show_ratings=SHOW_RATINGS,
    show_average=SHOW_AVERAGE,
    compact=False,
    add=True,
) -> str:
    """Converts a list of releases to a readable string."""

    releases_string: str = ""
    type_dict = {"album": [], "ep": [], "mixtape": []}
    artist_dict = {}

    for release in releases:
        dupe = False
        for artist in artist_dict:
            if artist == release.artist:
                dupe = True

        if not dupe:
            artist_dict[release.artist] = {"album": [], "ep": [], "mixtape": []}

        artist_dict[release.artist][release.type].append(release)

    increment = 1
    for artist in artist_dict:
        if not compact and len(releases_string) == 0:
            releases_string += artist
        elif not compact:
            releases_string += f"\n\n{artist[:CHAR_CAP]}"

        for type_list in artist_dict[artist].items():
            type_name = _capitalize_release_type(type_list[0])
            releases = type_list[1]

            if not compact and len(releases) > 0:
                releases_string += f"\n  {type_name}"

            for release in releases:
                if not compact:
                    releases_string += (
                        f"\n%2d  {release.title[:CHAR_CAP]} [{release.year}]"
                        % (increment)
                    )
                    increment += 1

                    if show_ratings and add:
                        releases_string += f": {release.ratings} ratings"
                    if show_average and add:
                        releases_string += f" ({release.average})"
                    if release_to_dict(release) in CURRENT_CHECKLIST_JSON["completed"]:
                        releases_string += " (Completed)"
                    if (
                        release_to_dict(release) in CURRENT_CHECKLIST_JSON["to-do"]
                        and add == True
                    ):
                        releases_string += " (In Checklist)"
                else:
                    new_line = "\n"
                    if len(releases_string) == 0:
                        new_line = ""
                    releases_string += f"{new_line}{release.artist[:CHAR_CAP]} - {release.title[:CHAR_CAP]} [{release.year}]"

    return releases_string


def add_releases(releases: List[Release]) -> List[bool]:
    """Add a release entry to the current checklist."""

    added = []
    for release in releases:
        added.append(add_release(release))

    return added


def add_release(release: Release) -> bool:
    """Adds a release to 'to-do'"""

    releases_list: List[Release] = (
        CURRENT_CHECKLIST_JSON["to-do"] + CURRENT_CHECKLIST_JSON["completed"]
    )

    dupe = False
    for release_entry in releases_list:
        if release.link == release_entry["link"]:
            dupe = True

    if dupe:
        return False

    todo_list: List[Release] = CURRENT_CHECKLIST_JSON["to-do"]
    todo_list.append(release_to_dict(release))

    # edited_checklist_json = CURRENT_CHECKLIST_JSON.copy()
    # edited_checklist_json["to-do"] = todo_list
    with open(CURRENT_CHECKLIST_FILE, "w") as checklist:
        checklist.write(json.dumps(CURRENT_CHECKLIST_JSON, indent=2))

    return True


def list_checklists(mark_current=True) -> Optional[List]:
    """Returns a list of checklist names from the checklists folder."""

    checklist_list = []
    config_json = CONFIG_JSON

    if not CHECKLIST_DIR.exists():
        return None

    for checklist in CHECKLIST_DIR.iterdir():
        if not checklist.is_file():
            continue

        checklist_name = checklist.name.strip(".json")

        if mark_current and checklist_name == config_json["current"]:
            checklist_list.append(f"{checklist_name} (Current)")
        else:
            checklist_list.append(checklist_name)

    return checklist_list


def view_artist(artist: str) -> bool:
    """Place an artist's releases in 'viewing'"""

    artist_link = ""
    for release in (
        CURRENT_CHECKLIST_JSON["to-do"] + CURRENT_CHECKLIST_JSON["completed"]
    ):
        if release["artist"].lower() == artist.lower():
            artist_link = release["artist_link"]
            break

    viewing = []
    for release in (
        CURRENT_CHECKLIST_JSON["to-do"] + CURRENT_CHECKLIST_JSON["completed"]
    ):
        if release["artist_link"] == artist_link:
            viewing.append(release)

    if not viewing:
        return False

    viewing.sort(key=lambda x: int(x["year"]))
    viewing.sort(key=lambda x: x["type"])

    CURRENT_CHECKLIST_JSON["viewing"] = viewing

    with open(CURRENT_CHECKLIST_FILE, "w") as current_checklist:
        current_checklist.write(json.dumps(CURRENT_CHECKLIST_JSON, indent=2))

    return True


def view_random() -> bool:
    if len(CURRENT_CHECKLIST_JSON["to-do"]) == 0:
        return False

    random_release = [random.choice(CURRENT_CHECKLIST_JSON["to-do"])]
    CURRENT_CHECKLIST_JSON["viewing"] = random_release

    with open(CURRENT_CHECKLIST_FILE, "w") as current_checklist:
        current_checklist.write(json.dumps(CURRENT_CHECKLIST_JSON, indent=2))

    return True


def view_random_artist():
    while True:
        random_release = random.choice(CURRENT_CHECKLIST_JSON["to-do"])
        random_artist_link = random_release["artist_link"]

        for release in CURRENT_CHECKLIST_JSON["viewing"]:
            if release["artist_link"] == random_artist_link:
                continue
        else:
            break


def check_release(release: Dict):
    """Moves a release from to-do to completed"""

    if not release in CURRENT_CHECKLIST_JSON["to-do"]:
        return False

    CURRENT_CHECKLIST_JSON["completed"].append(release)
    CURRENT_CHECKLIST_JSON["to-do"].remove(release)

    with open(CURRENT_CHECKLIST_FILE, "w") as checklist:
        checklist.write(json.dumps(CURRENT_CHECKLIST_JSON, indent=2))
    
    return True


def sanitize(string: str) -> str:
    return re.sub(r"[^\w_. -]", "_", string).lower().strip()


# Debug
if __name__ == "__main__":
    releases1 = rymapi.get_artist_releases("Sematary-1", ["album", "ep", "mixtape"])
    releases2 = rymapi.get_artist_releases("Aphex Twin", ["album", "ep", "mixtape"])
    print(releases_to_string(releases2 + releases1))
