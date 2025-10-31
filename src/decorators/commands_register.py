"""Submodule to register commands and their info"""
import logging


def command(cmd_name: str, flags: list[str] | None = None):
    """
    Decorator to register a class as a command
    :param cmd_name: name of the command
    :param flags: list of flags to be parsed(with '-' in the beginning)
    """
    def decorator(cls):
        setattr(cls, 'name', cmd_name)
        setattr(cls, 'logger', logging.getLogger(cmd_name))
        setattr(cls, 'flags', flags)
        return cls
    return decorator

def display_in_help(name: str | None = None):
    """
    Decorator to register method in display of '--help' option. Will take information from __doc__
    :param name: name to be displayed. If None, will take method name
    """
    def decorator(func):
        func.__display_help__ = True
        if name:
            func.__help_name__ = name
        return func
    return decorator
