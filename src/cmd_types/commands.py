import inspect
import logging
from abc import ABC, abstractmethod
from src.extra import utils
import src.decorators.commands_register as cmd_register


class ExecutableCommand(ABC):

    logger: logging.Logger
    name: str

    def __init__(self, args: list[str]):
        self.args = args


    def _log_error(self, msg):
        """Logs an error"""
        utils.log_error(msg, logger=self.logger)

    @abstractmethod
    def _parse_args(self, *args):
        """Parses command line arguments"""

    @abstractmethod
    def execute(self):
        """Executes command"""

    @cmd_register.display_in_help
    def help(self, *args, **kwargs):

        """Display this message"""

        outs: list[tuple[str, str]] = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and not name.startswith("__"):
                if getattr(obj, "__display_help__", False):
                    outs.append((name, getattr(obj, "__doc__", "")))
        output = ""
        max_len_tup = max(outs, key=lambda x: len(x[0]))
        max_len = len(max_len_tup[0])
        for out in outs:
            output += out[0] + " " * (max_len - len(out[0])) + 2 * "\t" + out[1] + "\n"

        return output


class UndoableCommand(ExecutableCommand, ABC):
    @abstractmethod
    def undo(self):
        """Undoes command"""
