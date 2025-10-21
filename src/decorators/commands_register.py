import logging


def command(cmd_name: str):
    def decorator(cls):
        setattr(cls, 'name', cmd_name)
        setattr(cls, 'logger', logging.getLogger(cmd_name))
        return cls
    return decorator

def display_in_help(name: str | None = None):
    def decorator(func):
        func.__display_help__ = True
        if name:
            func.__help_name__ = name
        return func
    return decorator
