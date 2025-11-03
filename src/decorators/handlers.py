"""Defines custom exception handlers"""
import inspect
from functools import wraps
import src.constants as cst
from src.cmd_types.output import CommandOutput
from src.extra.formatter import formatter

def get_cls_caller(func):
    """
    Gets initial caller of the decorated function. Caller is identified by logger attribute availability
    :param func: decorated function
    :return:
    """
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
    """Converts default exceptions to custom ones. Will raise an exception, if initial caller is class, not a function"""
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
            return CommandOutput(
                stderr = err_msg+"\n",
                errcode = err_msg_format.errcode
            )

    return wrapper
