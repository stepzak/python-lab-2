import logging
import os
import shlex
import readline #type: ignore
from pathlib import Path
import src.constants as cst
from src.cmd_types.meta import CommandMetadata
from src.extra import utils
from src.extra.plugins_loader import PluginLoader
from src.extra.utils import log_error
from src.plugins.plugin_default import LsCommand

HANDLED_ERRORS = tuple(cst.ERROR_HANDLERS_MESSAGES_FORMATS.keys())

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

    @staticmethod
    def fetch_name_and_args(splitted: list):
        if not splitted:
            return '', []
        cmd_name = splitted[0]
        if len(splitted) < 2:
            return cmd_name, []
        return cmd_name, splitted[1:]

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

    def parse_line(self, line: str):
        args = self.shlex_split(line)
        if not args:
            return None
        cmd_name, cmd_args = self.fetch_name_and_args(splitted=args)

        return cmd_name, cmd_args

    def execute_command(self, line: str):
        parsed = self.parse_line(line)
        if not parsed:
            return None

        cmd_name, cmd_args = parsed


        cmd_meta = self.cmd_map.get(cmd_name)
        if not cmd_meta:
            utils.write_history(line)
            utils.log_error(f"{cmd_name}: command not found", self.logger)
            return None

        self.logger.info(line)
        cmd_obj = cmd_meta.cmd(args = cmd_args)
        cmd_obj.history()

        if "--help" in cmd_args:
            return cmd_obj.help() #TODO: --help keys

        try:
            return cmd_obj.handled_run()
        except HANDLED_ERRORS as e:
            log_error(f"{cmd_name}: {str(e)}", self.logger)
