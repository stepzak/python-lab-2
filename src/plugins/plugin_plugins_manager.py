import inspect
from src.cmd_types.commands import ExecutableCommand
from src.decorators import commands_register as cmd_register

__author__ = "default"
__version__ = "1.0.0"

@cmd_register.command("plugins", flags=["-s"])
class PluginsCommand(ExecutableCommand):
    def _parse_args(self):
        flags = self.parse_flags()
        strict = flags["-s"]
        if not self.args:
            return "help", strict

        return self.args[-1], strict

    @cmd_register.display_in_help()
    def extra_long_title_that_does_nothing(self):
        """Bla bla bla"""
        return

    @cmd_register.display_in_help()
    def reload(self, strict):
        """Reloads plugins. --strict to raise error when failed to import"""

        caller_frame = inspect.currentframe().f_back

        while not getattr(caller_frame.f_locals["self"], "load_modules", None):
            caller_frame = caller_frame.f_back

        caller_obj = caller_frame.f_locals["self"]

        self.logger.debug("Reloading plugins...")

        caller_obj.load_modules(strict)

        self.logger.debug("Done reloading plugins")

    def execute(self):
        action, strict = self._parse_args()

        f = getattr(self, action, None)

        if getattr(f, "__display_help__", False):
            return f(strict)

        self._log_error(f"Unknown action: {action}")
        return None
