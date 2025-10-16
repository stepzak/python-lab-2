import inspect
import logging
import os
import shlex
import readline #type: ignore
from pathlib import Path
import src.constants as cst
from src.cmd_types.meta import CommandMetadata
from src.extra import utils
import src.decorators.commands_register as cmd_register
from src.extra.plugins_loader import PluginLoader
from src.cmd_types.commands import ExecutableCommand

@cmd_register.command("reload-plugins")
class ReloadPluginsCommand(ExecutableCommand):
    def _parse_args(self):
        print(self.args)
        if "--strict" in self.args or "-s" in self.args:
            self.logger.debug("Set strict_load to 'True'")
            return True
        self.logger.debug("Set strict_load to 'False'")
        return False

    def execute(self):
        strict = self._parse_args()
        caller_frame = inspect.currentframe().f_back
        caller_obj: CommandLineSession = caller_frame.f_locals["self"]

        caller_obj.load_modules(strict)

class CommandLineSession:
    def __init__(self, default_wd: str = cst.DEFAULT_PWD,
                 plugins_dir: str = cst.PLUGINS_DIR,
                 plugins_prefix: str = cst.PLUGINS_PREFIX,
                 strict_load: bool = cst.STRICT_PLUGIN_LOADING
                 ):
        self.default_wd = default_wd or "."
        self.cmd_map: dict[str, CommandMetadata] = {}
        self.plugins_dir = plugins_dir
        self.plugins_prefix = plugins_prefix
        self.logger = logging.getLogger(__name__)
        self.strict_load = strict_load

    def start_session(self):
        self.load_modules()
        default = self.default_wd
        to_move = Path(default).expanduser()
        os.chdir(to_move)
        while True:
            cmd = input(f"{os.getcwd()} $ ").strip()
            if not cmd.strip():
                continue
            try:
                res = self.execute_command(cmd)
                if res:
                    print(res)
            except Exception as e:
                name = shlex.split(cmd)[0]
                cmd_meta = self.cmd_map.get(name)
                if cmd_meta.plugin_author != "default":
                    utils.log_error(
                        f"Author of plugin '{cmd_meta.plugin_name}' of version '{cmd_meta.plugin_version}' is a debil(real name - '{cmd_meta.plugin_author}'). His command '{name}' raised an unexpected error:",
                        self.logger
                    )
                    utils.log_error(e, self.logger, exc=True)
                else:
                    raise

    def load_modules(self, outer_strict = None):
        if not outer_strict:
            outer_strict = self.strict_load
        plugins_loader = PluginLoader(self.plugins_dir, self.plugins_prefix, outer_strict)
        plugins_loader.load_plugins()

        self.cmd_map = plugins_loader.commands
        self.cmd_map["reload-plugins"] = CommandMetadata("reload-plugins", "default_plugin", "default", "1.0.0", ReloadPluginsCommand)

    def execute_command(self, line: str):
        args = shlex.split(line)
        if not args:
            return None
        cmd_name = args[0]
        if len(args) == 1:
            cmd_args = []
        else:
            cmd_args = args[1:]

        if "-h" in args or "--help" in args:
            return "Help placeholder..." #TODO: -h, --help keys

        cmd_meta = self.cmd_map.get(cmd_name)
        if not cmd_meta:
            utils.log_error(f"{args[0]}: command not found", self.logger)
            return None

        self.logger.info(line)
        return cmd_meta.cmd(args=cmd_args).execute()
