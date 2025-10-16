from src.cmd_types.commands import ExecutableCommand
from src.extra.decorators import command

__author__ = "krivoruchka"
__version__ = "0.1.0"

@command("xd")
class CommandXD(ExecutableCommand):
    def _parse_args(self, *args):
        return []

    def execute(self):
        raise Exception("Razrabotchik krivorukiy")

@command("ls")
class CommandLs(ExecutableCommand):
    def _parse_args(self, *args):
        pass

    def execute(self):
        pass
