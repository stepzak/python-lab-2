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

    """
    IO stream handler.

    :param default_wd: Default working directory.
    :type default_wd: str | Path

    :param plugins_dir: Directory to look for plugins.
    :type plugins_dir: str | Path

    :param plugins_prefix: Prefix that plugins file must start with
    :type plugins_prefix: str

    :param strict_load: If set to False, will not raise any error while importing plugins
    :type strict_load: bool
    """

    def __init__(self, default_wd: str | Path = cst.DEFAULT_PWD,
                 plugins_dir: str = cst.PLUGINS_DIR,
                 plugins_prefix: str = cst.PLUGINS_PREFIX,
                 strict_load: bool = cst.STRICT_PLUGIN_LOADING
                 ):
        self.default_wd = default_wd or "."
        self.cmd_map: dict[str, CommandMetadata] = {}
        """Map of commands names to its metadata."""

        self.plugins_dir = plugins_dir
        self.plugins_prefix = plugins_prefix
        self.logger = logging.getLogger(__name__)
        self.strict_load = strict_load

        self.posix = utils.is_posix()
        """Is system posix"""

    def shlex_split(self, cmd: str) -> list[str]:
        """
        Splits a line like bash does(with passed posix param)
        :param cmd: Input line(command)
        :return: List of split: command name is the first element, the next ones are args
        """
        return shlex.split(cmd, posix=self.posix)

    @staticmethod
    def fetch_name_and_args(splitted: list) -> tuple[str, list[str]]:
        """
        Gets command name and args from shlex split line
        :param splitted: shlex split line
        :return: command name, args
        """
        if not splitted:
            return '', []
        cmd_name = splitted[0]
        if len(splitted) < 2:
            return cmd_name, []
        return cmd_name, splitted[1:]

    def start_session(self):
        """
        Starts an infinite loop of commandline session
        :return: None
        """
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
                    res = res.strip()
                    if res.stderr:
                        errs = res.stderr.split("\n")
                        for err in errs:
                            if not err:
                                continue
                            cmd_name = self.parse_line(cmd)[0]
                            log_error(f"{cmd_name}: {err}", self.logger)
                    if res.stdout:
                        print(res.stdout)
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

    def load_modules(self, outer_strict: bool = False):
        """
        Loads plugins
        :param outer_strict: if method was called out of class, will be more prioritized than self.strict_load
        :type outer_strict: bool

        :return: None
        """

        if not outer_strict:
            outer_strict = self.strict_load
        plugins_loader = PluginLoader(self.plugins_dir, self.plugins_prefix, outer_strict)
        plugins_loader.load_plugins()

        self.cmd_map = plugins_loader.commands
        #self.cmd_map["reload-plugins"] = CommandMetadata("reload-plugins", "default_plugin", "default", "1.0.0", ReloadPluginsCommand)

    def parse_line(self, line: str) -> tuple[str, list[str]] | None:
        """
        Parses input line by calling self.shlex_split and self.fetch_name_and_args
        :param line: Input line
        :return: command name, args | None, if line was empty
        """
        args = self.shlex_split(line)
        if not args:
            return None
        cmd_name, cmd_args = self.fetch_name_and_args(splitted=args)

        return cmd_name, cmd_args

    def execute_command(self, line: str):
        """
        Executes input command
        :param line:
        :return: Result of command(None, if error occurred or command was not found)
        """
        parsed = self.parse_line(line)
        if not parsed:
            return None

        cmd_name, cmd_args = parsed
        if cmd_name == "help":
            out = ""
            for cmd in sorted(self.cmd_map.keys()):
                out+=f"{cmd}\n"
            return out


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
