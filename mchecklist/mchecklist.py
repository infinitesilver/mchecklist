import json
from pathlib import Path


def _get_checklist_path(name: str) -> Path:
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    return Path(f"{source_dir}/checklists/{name}.json")

def init_database(name="") -> None:
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    Path(f"{source_dir}/checklists").mkdir(exist_ok=True)
    checklists_dir = Path(f"{source_dir}/checklists")
    checklist = open(f"{checklists_dir}/{name}.json")
    checklist.close()


# Debug
    init_database("checklist1")
