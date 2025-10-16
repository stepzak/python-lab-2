import logging
from pathlib import Path


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
