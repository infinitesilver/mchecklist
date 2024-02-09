import json
from pathlib import Path
from pathlib import PurePath
from typing import Optional, Dict, List
import re
from mchecklist.rymapi import ArtistReleases


def _get_checklist_path(name: str) -> Optional[Path]:
    source_dir = _get_source_dir()
    if source_dir.joinpath("checklists", f"{name}.json").exists():
        return source_dir.joinpath("checklists", f"{name}.json")
    else:
        return None
    

def _get_checklist_dir() -> Path:
    source_dir = _get_source_dir()
    return source_dir.joinpath("checklists")


def _get_source_dir() -> Path:
    source_path = Path(__file__).resolve()
    return source_path.parent


def _get_config_json() -> Dict:
    with open(_get_source_dir().joinpath("config.json")) as config_file:
         return json.load(config_file)


def checklist_exists(checklist_name: str) -> bool:
    return _get_checklist_path(checklist_name)


def init_checklist(name="") -> Optional[str]:
    """Create a new JSON file for a checklist. Called by create."""

    source_dir = _get_source_dir()

    source_dir.joinpath("checklists").mkdir(exist_ok=True)
    checklists_dir = source_dir.joinpath("checklists")

    # If no name argument was passed
    if not name:
        counter = 1
        while checklist_exists(f"checklist{counter}"):
            counter += 1
        
        open(checklists_dir.joinpath(f"checklist{counter}.json"), "x")
        returned_name = f"checklist{counter}"
    else:
        sanitized_name = sanitize(name)

        # If a checklist with the same name already exists
        if checklist_exists(sanitized_name):
            return None

        open(checklists_dir.joinpath(f"{sanitized_name}.json"), "x")
        returned_name = sanitized_name

    # Edit config

    if source_dir.joinpath("config.json").exists():
        with open(source_dir.joinpath("config.json")) as config_file:
            config_json = json.load(config_file)
    else:
        config_json = {}

    config_json["Current"] = returned_name

    with open(source_dir.joinpath("config.json"), "w") as config_file:
        config_file.write(json.dumps(config_json, indent=2))
    
    # Edit new checklist
    checklist_json = {"Releases": []}
    with open(checklists_dir.joinpath(f"{returned_name}.json"), "w") as checklist_file:
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
        return sanitized_new_name
    else:
        return None


def delete_checklist(name: str) -> Optional[str]:
    """Deletes a checklist's JSON file. Called by delete."""

    checklist_path = _get_checklist_path(name)

    if checklist_path:
        checklist_path.unlink()

        config_json = _get_config_json()
        config_json["Current"] = ""
        return name
    else:
        return None


def releases_to_string(artist_releases: ArtistReleases) -> Optional[str]:
    if not _get_source_dir().joinpath("config.json").exists():
        return None

    current_checklist_name = _get_config_json()["Current"]


def list_checklists() -> List:
    checklist_list = []

    for checklist in _get_checklist_dir().iterdir():
        if checklist.is_file():
            checklist_list.append(checklist.name.strip(".json"))
    
    return checklist_list


def sanitize(string: str) -> str:
    return re.sub(r"[^\w_. -]", "_", string).lower().strip()


# Debug
if __name__ == "__main__":
    print(list_checklists())
