import grp
import os
import pwd
import shutil
import stat
import time
from pathlib import Path
import src.decorators.commands_register as cmd_register
import src.decorators.handlers as handlers
import src.extra.utils as utils
import src.cmd_types.commands as cmds

__author__ = "default"
__version__ = "1.0.0"

@cmd_register.command("ls")
class LsCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[Path, bool]:
        args = list(self.args)
        no_l = utils.remove_arg("-l", args)
        l_flag = True
        if len(no_l) == len(args):
            l_flag = False
        if len(no_l) == 0:
            no_l.insert(0, ".")
        path = Path(no_l[0])
        path = Path.expanduser(path)

        return path, l_flag

    @handlers.handle_all_default
    def execute(self):
        path, l_flag = self._parse_args()
        out = ""
        path_iter = path.iterdir()

        for item in path_iter:
            if l_flag:
                stat_info = item.stat()
                permissions = stat.filemode(stat_info.st_mode)
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
                out += f"{permissions} {stat_info.st_nlink:>2} {owner} {group} {stat_info.st_size:>8} {time.strftime('%b %d %H:%M', time.gmtime(stat_info.st_mtime))} {item.name} \n"

            else:
                out += f"{item.name} "
        return out.strip()

@cmd_register.command("cd")
class CdCommand(cmds.ExecutableCommand):

    def _parse_args(self) -> Path:

        args = self.args
        if not args:
            args.insert(0, "~/")
        path = args[0]
        path_obj = utils.create_path_obj(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj

        return path_obj

    @handlers.handle_all_default
    def execute(self):
        path = self._parse_args()
        if path.is_dir():
            os.chdir(path)
            return None
        elif path.is_file():

            msg = f"{path}: it is a file"
            self._log_error(msg)
            return None
        raise FileNotFoundError(2, f"Not found: {path}", path)


@cmd_register.command("cat")
class CatCommand(cmds.ExecutableCommand):

    def _parse_args(self) -> Path:
        f = self.args[0]
        path_obj = utils.create_path_obj(f)
        return path_obj

    @handlers.handle_all_default
    def execute(self):
        path_obj = self._parse_args()
        if path_obj.is_dir():
            msg = f"{path_obj}: is is a directory"
            self._log_error(msg)
        elif path_obj.is_file():
            with open(path_obj, "r") as file:
                return file.read()
        return None

@cmd_register.command("cp")
class CopyCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[Path, Path, bool]:
        args = self.args
        no_r = utils.remove_arg("-r", args)
        r = True
        if len(no_r) == len(args):
            r = False

        source_dir = utils.create_path_obj(no_r[0])
        to_dir = utils.create_path_obj(no_r[1])

        return source_dir, to_dir, r

    @handlers.handle_all_default
    def execute(self):
        source_dir, to_dir, r = self._parse_args()
        if source_dir.is_dir():
            if not r:
                self._log_error(f"-r option was not specified: {source_dir} is ignored")
                return None
            shutil.copytree(source_dir, to_dir, dirs_exist_ok=True)
            return None

        shutil.copy(source_dir, to_dir)
        return None
