import logging
import os
import shutil
from pathlib import Path
import src.constants as cst

def log_error(msg: str | Exception, logger: logging.Logger, exc = False) -> None:
    print(msg)
    if exc:
        logger.exception(msg)
        return
    logger.error(f"ERROR: {msg}")

def remove_arg(arg: str, args: list) -> list:
    c_args = args.copy()
    while arg in c_args:
        c_args.remove(arg)
    return c_args

def create_path_obj(path: str, must_exist = True) -> Path:
    path_obj = Path(path)
    path_obj = path_obj.expanduser()

    if not path_obj.exists() and must_exist:
        raise FileNotFoundError(
            2,
            "File not found",
            str(path)
        )
    return path_obj

def write_history(obj: str):
    if not cst.HISTORY_PATH.exists():
        cst.HISTORY_PATH.touch()
    with open(cst.HISTORY_PATH, "a") as f:
        f.write(f"{obj}\n")

def is_posix():
    return os.name == "posix"

def get_terminal_dimensions():
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24

def raise_on_strict(logger, exc, strict: bool = False):
    if strict:
        raise exc
    log_error(str(exc), logger)
