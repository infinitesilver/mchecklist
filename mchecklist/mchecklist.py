import json
from pathlib import Path
from typing import Optional, Dict, List
import re
from rymapi import Artist, Release


SOURCE_DIR = Path(__file__).resolve().parent
CHECKLIST_DIR = SOURCE_DIR.joinpath("checklists")
CONFIG_FILE = SOURCE_DIR.joinpath("config.json")


def _get_checklist_path(name: str) -> Optional[Path]:
    if checklist_exists(name):
        return CHECKLIST_DIR.joinpath(f"{name}.json")
    else:
        return None


def _get_config_json() -> Dict:
    with open(CONFIG_FILE) as config_file:
        return json.load(config_file)


def _get_current_checklist() -> str:
    with open(CONFIG_FILE) as config_file:
        return json.load(config_file)["Current"]


def _write_to_config(config_json) -> None:
    with open(CONFIG_FILE, "w") as config_file:
        config_file.write(json.dumps(config_json, indent=2))


def _capitalize_release_type(release_type: str) -> str:
    match(release_type):
        case("album"):
            return "Album"
        case("ep"):
            return "EP"
        case("mixtape"):
            return "Mixtape"
        case _:
            raise ValueError("Not a valid release type")


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

    config_json["Current"] = returned_name

    _write_to_config(config_json)

    # Edit new checklist
    checklist_json = {"Genres": genres, "Releases": []}

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

        config_json = _get_config_json()
        if config_json["Current"] == old_name:
            config_json["Current"] = sanitized_new_name
            _write_to_config(config_json)

        return sanitized_new_name
    else:
        return None


def delete_checklist(name: str) -> Optional[str]:
    """Deletes a checklist's JSON file. Called by delete."""

    checklist_path = _get_checklist_path(name)

    if checklist_path:
        checklist_path.unlink()

        config_json = _get_config_json()

        if config_json["Current"] == name:
            config_json["Current"] == ""
            with open(CONFIG_FILE) as config_file:
                config_file.write(json.dumps(config_json))

        return name
    else:
        return None


def releases_to_string(artist: Artist, show_ratings=False, show_average=False) -> str:
    """Converts a list of releases to a readable string."""

    releases_string: str = artist.name
    type_dict = {"album": [], "ep": [], "mixtape": []}

    for release in artist.releases:
        type_dict[release.type].append(release)

    for type_list in type_dict.items():
        type_name = _capitalize_release_type(type_list[0])
        releases = type_list[1]
        releases_string += f"\n  {type_name}"
        for release in releases:
            releases_string += f"\n    {release.title} [{release.year}]"
            if show_ratings:
                releases_string += f": {release.ratings} ratings"
            if show_average:
                releases_string += f" ({release.average})"

    return releases_string


def add_release(release: Release) -> bool:
    """Add a release entry to the current checklist."""

    current_checklist_path = _get_checklist_path(_get_current_checklist())
    with open(current_checklist_path) as checklist:
        checklist_json: Dict = json.load(checklist)
        releases_list: List[Release] = checklist["Releases"]
    
    for release_entry in releases_list:
        if release == release_entry:
            return False
    
    releases_list.append(release)
    checklist_json["Releases"] = releases_list
    with open(current_checklist_path, 'w') as checklist:
        checklist.write(json.dumps(checklist_json))
    
    return True


def list_checklists(mark_current=True) -> Optional[List]:
    """Returns a list of checklist names from the checklists folder."""

    checklist_list = []
    config_json = _get_config_json()

    if not CHECKLIST_DIR.exists():
        return None

    for checklist in CHECKLIST_DIR.iterdir():
        if not checklist.is_file():
            continue

        checklist_name = checklist.name.strip(".json")

        if mark_current and checklist_name == config_json["Current"]:
            checklist_list.append(f"{checklist_name} (Current)")
        else:
            checklist_list.append(checklist_name)

    return checklist_list


def sanitize(string: str) -> str:
    return re.sub(r"[^\w_. -]", "_", string).lower().strip()


# Debug
if __name__ == "__main__":
    print(list_checklists())
