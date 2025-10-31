import logging
import os
import shlex
import readline #type: ignore
from pathlib import Path
import src.constants as cst
from src.cmd_types.meta import CommandMetadata
from src.decorators.handlers import HANDLED_ERRORS
from src.extra import utils
from src.extra.plugins_loader import PluginLoader
from src.extra.utils import log_error
from src.plugins.plugin_default import LsCommand


class CommandLineSession:
    def __init__(self, default_wd: str | Path = cst.DEFAULT_PWD,
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
        self.posix = utils.is_posix()

    def shlex_split(self, cmd: str):
        return shlex.split(cmd, posix=self.posix)

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

            except ImportError:
                raise

            except Exception as e:
                try:
                    name = self.shlex_split(cmd)[0]
                    cmd_meta = self.cmd_map.get(name)
                except ValueError:
                    name = ''
                    cmd_meta = CommandMetadata('default', 'default', 'default', '', LsCommand)
                if cmd_meta.plugin_author != "default":
                    utils.log_error(
                        f"Author of plugin '{cmd_meta.plugin_name}' of version '{cmd_meta.plugin_version}' is a debil(real name - '{cmd_meta.plugin_author}'). His command '{name}' raised an unexpected error:",
                        self.logger
                    )
                    utils.log_error(e, self.logger, exc=True)
                else:
                    utils.log_error(e, self.logger)

    def load_modules(self, outer_strict = None):
        if not outer_strict:
            outer_strict = self.strict_load
        plugins_loader = PluginLoader(self.plugins_dir, self.plugins_prefix, outer_strict)
        plugins_loader.load_plugins()

        self.cmd_map = plugins_loader.commands
        #self.cmd_map["reload-plugins"] = CommandMetadata("reload-plugins", "default_plugin", "default", "1.0.0", ReloadPluginsCommand)



    def execute_command(self, line: str):
        args = self.shlex_split(line)
        if not args:
            return None
        cmd_name = args[0]
        if len(args) == 1:
            cmd_args = []
        else:
            cmd_args = args[1:]

        if "--help" in args:
            return "Help placeholder..." #TODO: --help keys

        cmd_meta = self.cmd_map.get(cmd_name)
        if not cmd_meta:
            utils.write_history(line)
            utils.log_error(f"{args[0]}: command not found", self.logger)
            return None

        self.logger.info(line)
        cmd_obj = cmd_meta.cmd(args = cmd_args)
        cmd_obj.history()
        try:
            return cmd_obj.handled_run()
        except HANDLED_ERRORS as e:
            log_error(f"{cmd_name}: {str(e)}", self.logger)
