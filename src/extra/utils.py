import logging
import os
import shutil
from pathlib import Path
import src.constants as cst

def log_error(msg: str | Exception, logger: logging.Logger, exc = False) -> None:
    """
    Writes an error message to stdout and logfile
    :param msg: message to log
    :param logger: logger to write with
    :param exc: if set to True will enable full traceback
    """
    print(msg)
    if exc:
        logger.exception(msg)
        return
    logger.error(f"ERROR: {msg}")

def remove_arg(arg: str, args: list) -> list:
    """
    Remove argument from list of args. Common usage: flags parsing

    :param arg: argument to remove
    :param args: list of arguments to remove from
    :return: list of arguments after removal
    """
    c_args = args.copy()
    while arg in c_args:
        c_args.remove(arg)
    return c_args

def create_path_obj(path: str, must_exist = True) -> Path:
    """
    Create pathlib.Path object from string.
    :param path: path to create object from
    :param must_exist: if set to True, will raise exception if path doesn't exist
    :raise FileNotFoundError: if path doesn't exist ans must_exist set to True
    :return: pathlib.Path object
    """
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
    """
    Write to history file
    :param obj: line to write to history
    """
    if not cst.HISTORY_PATH.exists():
        cst.HISTORY_PATH.touch()
    with open(cst.HISTORY_PATH, "a", encoding='utf-8') as f:
        f.write(f"{obj}\n")

def is_posix() -> bool:
    """
    Check if system is on posix
    :return: True if it is on posix, False otherwise
    """
    return os.name == "posix"

def get_terminal_dimensions() -> tuple[int, int]:
    """
    Get terminal dimensions
    :return: terminal columns, terminal lines
    """
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24

def raise_on_strict(logger, exc, strict: bool = False):
    """
    Raise exception if strict is True
    :param logger: logger
    :param exc: exception to raise
    :param strict: will raise exc if True. Otherwise, will call log_error(exc, logger)
    :return:
    """
    if strict:
        raise exc
    log_error(str(exc), logger)
