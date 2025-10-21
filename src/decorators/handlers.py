import inspect
from functools import wraps

from src.extra.utils import log_error

def get_cls_caller(func):
    @wraps(func)
    def wrapper(self = None, *args, **kwargs):
        requires_self = True
        if not getattr(self, 'logger', None):
            requires_self = False
            caller_frame = inspect.currentframe().f_back
            while not (
                    getattr(caller_frame.f_locals.get('self', {}),
                            "logger",
                            None)
            ):
                caller_frame = caller_frame.f_back
            args = list(args)
            args.insert(0, self)
            self = caller_frame.f_locals["self"]

        return func(self, *args, requires_self = requires_self, **kwargs)
    return wrapper

def handle_not_found(func):
    @wraps(func)
    @get_cls_caller
    def wrapper(self, *args, requires_self: bool = True, **kwargs):
        try:
            if requires_self:
                return func(self,  *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except FileNotFoundError as e:
            log_error(f"No such file or directory: {e.filename}", self.logger)
            return None
    return wrapper

def handle_permission_denied(func):
    @wraps(func)
    @get_cls_caller
    def wrapper(self, *args, requires_self: bool = True, **kwargs):
        try:
            if requires_self:
                return func(self, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except PermissionError as e:
            log_error(f"{e.filename}: permission denied", self.logger)
            return None

    return wrapper

def handle_all_default(func):
    @wraps(func)
    @handle_permission_denied
    @handle_not_found
    @get_cls_caller
    def wrapper(self, *args, requires_self: bool = True, **kwargs):
        if requires_self:
            return func(self, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper
