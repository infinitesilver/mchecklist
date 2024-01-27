import json
from pathlib import Path
from pathlib import PurePath
from typing import Optional


def _get_checklist_path(name: str) -> Path:
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    return Path(f"{source_dir}/checklists/{name}.json")


def init_database(name="") -> Optional[str]:
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

    if not Path(checklists_dir).joinpath(f"{name}.json").exists():
        checklist = open(Path(checklists_dir).joinpath(f"{name}.json"), "w")
        checklist.close()
        return name
    else:
        return


# Debug
print(init_database())
