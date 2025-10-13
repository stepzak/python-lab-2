import logging
import os
import shlex
from pathlib import Path
import readline
import src.constants as cst
from src.cmd_types.autocompletes import basic_autocomplete
from src.extra import utils
from src.extra.plugins_loader import PluginLoader
from src.cmd_types.commands import ExecutableCommand

class CommandLineSession:
    def __init__(self, default_wd: str = cst.DEFAULT_PWD,
                 plugins_dir: str = cst.PLUGINS_DIR,
                 plugins_prefix: str = cst.PLUGINS_PREFIX):
        self.default_wd = default_wd or "."
        self.cmd_map: dict[str, type[ExecutableCommand]] = {}
        self.plugins_dir = plugins_dir
        self.plugins_prefix = plugins_prefix
        self.logger = logging.getLogger(__name__)

    def autocomplete(self, text: str, state: int):
        ret = []
        text = readline.get_line_buffer().lstrip()
        if " " not in text:
            for k in self.cmd_map.keys():
                if k.startswith(text):
                    ret.append(k)
        else:
            cmd_name = text.split(" ")
            cmd_obj = self.cmd_map.get(cmd_name[0])
            return cmd_obj.autocomplete(cmd_name[-1], state)[state]
        return ret[state]

    def start_session(self):
        self.load_modules()
        default = self.default_wd
        to_move = Path(default).expanduser()
        readline.set_completer(self.autocomplete)
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')
        os.chdir(to_move)
        while True:
            cmd = input(f"{os.getcwd()} $ ").strip()
            res = self.execute_command(cmd)
            if res:
                print(res)

    def load_modules(self):
        plugins_loader = PluginLoader(self.plugins_dir, self.plugins_prefix)
        plugins_loader.load_plugins()

        self.cmd_map = plugins_loader.commands

    def execute_command(self, line: str):
        args = shlex.split(line)
        if not args:
            return None
        cmd_name = args[0]
        if len(args) == 1:
            cmd_args = []
        else:
            cmd_args = args[1:]

        cmd_obj = self.cmd_map.get(cmd_name)
        if not cmd_obj:
            utils.log_error(f"{args[0]}: command not found", self.logger)
            return None
        self.logger.info(line)
        return cmd_obj(args=cmd_args).execute()



