import logging


def command(cmd_name: str):
    def decorator(cls):
        setattr(cls, 'name', cmd_name)
        setattr(cls, 'logger', logging.getLogger(cmd_name))
        return cls
    return decorator

def display_in_help(func):
    func.__display_help__ = True
    return func
