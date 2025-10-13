from pathlib import Path

def basic_autocomplete(text: str, state: int, files: bool = True, dirs: bool = True):
    ret = []
    path = Path(".")
    for f in path.iterdir():
        if f.name.startswith(text.strip()):
            if (f.is_file() or dirs) and (f.is_dir() or files):
                ret.append(f.name)
    return ret
