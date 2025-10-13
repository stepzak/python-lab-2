import logging
from functools import wraps

from src.extra.utils import log_error

def handle_not_found(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FileNotFoundError as e:
            log_error(f"No such file or directory: {e.filename}", self.logger)
            return None
    return wrapper

def command(cmd_name: str):
    def decorator(cls):
        setattr(cls, 'name', cmd_name)
        setattr(cls, 'logger', logging.getLogger(cmd_name))
        return cls
    return decorator