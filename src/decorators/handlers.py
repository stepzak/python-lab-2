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

def handle_permission_denied(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except PermissionError as e:
            log_error(f"{e.filename}: permission denied", self.logger)
            return None
    return wrapper

def handle_all_default(func):
    @wraps(func)
    @handle_permission_denied
    @handle_not_found
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs)
    return wrapper
