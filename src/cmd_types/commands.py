import logging
from abc import ABC, abstractmethod
from src.extra import utils

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


class UndoableCommand(ExecutableCommand, ABC):
    @abstractmethod
    def undo(self):
        """Undoes command"""
