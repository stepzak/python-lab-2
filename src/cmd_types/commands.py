"""Commands abstract classes defined here. You may register your own(see plugins.plugin_archives)"""

import inspect
import logging
from abc import ABC, abstractmethod

from src.decorators import handlers
from src.extra import utils
import src.decorators.commands_register as cmd_register


class ExecutableCommand(ABC):
    """
    Abstract class for executable commands(has no undo method)
    :param args: list of arguments passed to the command
    :type args: list[str]
    """

    logger: logging.Logger

    name: str
    """Name of the command"""

    flags: list | None
    """Flags names to parse(with '-' in front)"""

    def __init__(self, args: list[str]):
        self.args = args
        """List of arguments passed to the command"""


    def _log_error(self, msg):
        """
        Logs an error in format {name}: {msg}
        :param msg: error message
        :type msg: str
        """
        utils.log_error(self.name+": "+msg, logger=self.logger)

    def parse_flags(self) -> dict[str, bool]:
        """
        Parse the flags passed in the args
        :return: dict of {flag: True/False}
        :rtype: dict[str, bool]
        """
        parsed_flags = {}
        if self.flags:
            for flag in self.flags:
                no_flag = utils.remove_arg(flag, self.args)
                parsed_flags[flag] = (len(self.args) != len(no_flag))
                self.args = no_flag

        return parsed_flags

    def exec(self, line: str):
        """
        Executes a line in terminal. Be cautious
        :param line: line to execute
        :type line: str
        """
        cur_frame = inspect.currentframe()
        f_back = cur_frame.f_back #type: ignore
        while not getattr(f_back.f_locals["self"], 'execute_command', None): #type: ignore

            f_back = f_back.f_back #type: ignore
            if not f_back:
                break
        if f_back:
            return f_back.f_locals["self"].execute_command(line) #type: ignore
        return None

    @abstractmethod
    def _parse_args(self):
        """Parses command line arguments"""

    @abstractmethod
    def execute(self):
        """Executes command"""

    @cmd_register.display_in_help("--help")
    def help(self, *args, **kwargs):

        """Display this message"""

        outs: list[tuple[str, str]] = []
        for name, obj in inspect.getmembers(self):
            if inspect.ismethod(obj) and not name.startswith("__"):
                if getattr(obj, "__display_help__", False):
                    name_to_append = getattr(obj, "__help_name__", None) or name
                    doc = getattr(obj, "__doc__", "")
                    outs.append((name_to_append, doc))
        output = ""
        max_len_tup = max(outs, key=lambda x: len(x[0]))
        max_len = len(max_len_tup[0])
        for out in outs:
            output += out[0] + " " * (max_len - len(out[0])) + 2 * "\t" + out[1] + "\n"

        return output

    @handlers.handle_all_default
    def handled_run(self) -> str:
        """
        Runs a command with exception handlers, registered by default.
        You may create your own abstract class with this method overriden

        :return: command execution result
        :rtype: str
        """
        return self.execute()

    def history(self):
        """
        Writes command to history file
        """
        line = ' '.join([self.name]+self.args)
        utils.write_history(line)


class UndoableCommand(ExecutableCommand, ABC):

    """
    Abstract class for undoable commands(fields of ExecutableCommand are included)
    """

    @abstractmethod
    def undo(self):
        """Undoes command"""
