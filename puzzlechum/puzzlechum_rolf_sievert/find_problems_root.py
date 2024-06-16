from pathlib import Path

CHUM_ROOT_FOLDER_NAME = '.chum'

def find_problems_root() -> Path|None:
    cwd = Path.cwd()

    for parent in [cwd] + list(cwd.parents):
        if (parent / CHUM_ROOT_FOLDER_NAME).is_dir():
            return parent

    return None
