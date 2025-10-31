""""""
import inspect
from functools import wraps
import src.constants as cst
from src.extra.formatter import formatter
from src.extra.utils import raise_on_strict

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

def handle_all_default(func):
    @wraps(func)
    @get_cls_caller
    def wrapper(self, *args, requires_self: bool = True, **kwargs):
        try:
            if requires_self:
                return func(self, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except tuple(cst.ERROR_HANDLERS_MESSAGES_FORMATS.keys()) as e:
            e_type = type(e)
            err_msg_format = cst.ERROR_HANDLERS_MESSAGES_FORMATS[e_type]
            err_msg = formatter(e, err_msg_format)
            exc = e_type(err_msg)
            raise_on_strict(self.logger, exc, requires_self)

    return wrapper
