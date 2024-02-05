import json
from pathlib import Path
from pathlib import PurePath
from typing import Optional


def _get_checklist_path(name: str) -> Path:
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    return Path(source_dir).joinpath("checklists", f"{name}.json")


def init_database(name="") -> Optional[str]:
    """Create a new JSON file for a checklist. Called by create."""

    source_path = Path(__file__).resolve()
    source_dir = source_path.parent

    Path(source_dir).joinpath("checklists").mkdir(exist_ok=True)
    checklists_dir = Path(source_dir).joinpath("checklists")

    # If no name argument was passed
    if not name:
        counter = 1
        while Path(checklists_dir).joinpath(f"checklist{counter}.json").exists():
            counter += 1
        checklist = open(Path(checklists_dir).joinpath(f"checklist{counter}.json"), "w")
        checklist.close()
        return f"checklist{counter}"

    # If a checklist with the same name doesn't already exist
    if not Path(checklists_dir).joinpath(f"{name}.json").exists():
        checklist = open(Path(checklists_dir).joinpath(f"{name}.json"), "w")
        checklist.close()
        return name
    else:
        return

def rename_checklist(old_name: str, new_name: str) -> None:
    """Renames a checklist's JSON file. Called by edit."""

    checklist_path = _get_checklist_path(old_name)
    checklist_path.rename(f"{new_name}.json")


# Debug
print(init_database())
