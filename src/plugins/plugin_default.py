import grp
import inspect
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
from src.extra.utils import create_path_obj
import src.constants as cst

__author__ = "default"
__version__ = "1.0.0"

def get_resolved_line(args: list[str]) -> str:
    line = ""
    for arg in args:
        line += f" {create_path_obj(arg, must_exist=False).resolve()}"
    return line

@cmd_register.command("ls")
class LsCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[list[Path], bool]:
        args = list(self.args)
        no_l = utils.remove_arg("-l", args)

        ret = []

        l_flag = True
        if len(no_l) == len(args):
            l_flag = False
        if len(no_l) == 0:
            no_l.insert(0, ".")
        for arg in no_l:
            ret.append(create_path_obj(arg, must_exist=False))

        return ret, l_flag

    def execute(self):
        paths, l_flag = self._parse_args()
        out = ""

        @handlers.handle_all_default
        def file_info(item: Path):
            output = ""
            if l_flag:
                stat_info = item.stat()
                permissions = stat.filemode(stat_info.st_mode)
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
                output += f"{permissions} {stat_info.st_nlink:>2} {owner} {group} {stat_info.st_size:>8} {time.strftime('%b %d %H:%M', time.gmtime(stat_info.st_mtime))} {item.name} \n"

            else:
                output += f"{item.name} "
            return output


        @handlers.handle_all_default
        def list_dir(path: Path):
            output = ""

            if path.is_file():
                return file_info(path)

            if len(paths)>1:
                output = str(path) + ":\n"
            path_iter = path.iterdir()

            for item in path_iter:
                output += file_info(item)

            return output+"\n\n"

        for arg in paths:
            add = list_dir(arg)
            if add:
                out = out + add

        return out.strip()

@cmd_register.command("cd")
class CdCommand(cmds.ExecutableCommand):

    def _parse_args(self) -> tuple[Path, int]:

        args = self.args
        if not args:
            args.insert(0, "~/")

        if len(args)>1:
            return Path(""), len(args)

        path = args[0]
        path_obj = utils.create_path_obj(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj

        return path_obj, len(args)

    @handlers.handle_all_default
    def execute(self):
        path, n_args = self._parse_args()
        if n_args>1:
            self._log_error("too many arguments")
            return None
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
    def _parse_args(self) -> tuple[list[Path], Path, bool]:
        args = self.args
        no_r = utils.remove_arg("-r", args)
        r = True
        if len(no_r) == len(args):
            r = False
        if len(no_r)<2:
            self._log_error("too few arguments")
            print("'cp --help' to get more info")
        source_dirs = [utils.create_path_obj(o, must_exist=False) for o in no_r[:-1]]
        to_dir = utils.create_path_obj(no_r[-1], must_exist=False).expanduser()

        return source_dirs, to_dir, r

    def execute(self):
        source_dirs, to_dir, r = self._parse_args()

        @handlers.handle_all_default
        def copy(source: Path, to: Path):
            if source.is_dir():
                if not r:
                    self._log_error(f"-r option was not specified: '{source}' is ignored")
                    return None

                if to_dir.resolve().is_relative_to(source_dir.resolve()):
                    self._log_error(f"Unable to copy '{to}' to itself")
                    return None
                try:
                    shutil.copytree(source, to, dirs_exist_ok=True)
                except shutil.Error as e:
                    for arg in e.args[0]:
                        self._log_error(f"{arg[0]}: {arg[2]}")
                return None

            shutil.copy2(source, to)
            return None

        for source_dir in source_dirs:
            copy(source_dir, to_dir)

    def history(self):
        line = self.name
        no_r = utils.remove_arg("-r", self.args)
        line+=get_resolved_line(no_r)

        utils.write_history(line)

    def undo(self):
        source = Path(self.args.pop())
        for arg in self.args:
            move_from = source / Path(arg).name
            RemoveCommand([str(move_from)]).execute()

@cmd_register.command("mv")
class MoveCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[list[Path], Path]:
        args = self.args

        source_dirs = [utils.create_path_obj(o) for o in args[:-1]]
        to_dir = utils.create_path_obj(args[-1])

        return source_dirs, to_dir

    @handlers.handle_all_default
    def execute(self):
        source_dirs, to_dir = self._parse_args()
        for source_dir in source_dirs:
            if to_dir.resolve().is_relative_to(source_dir.resolve()):
                self._log_error(f"Unable to move '{source_dir}' to itself")
                continue
            shutil.move(source_dir, to_dir)
        return None

    def history(self):
        line = self.name
        line+=get_resolved_line(self.args)

        utils.write_history(line)

    def undo(self):
        source = Path(self.args.pop())
        for arg in self.args:
            move_from = source / Path(arg).name
            shutil.move(move_from, arg)


@cmd_register.command("rm")
class RemoveCommand(cmds.UndoableCommand):
    def _parse_args(self) -> tuple[list[Path], bool]:
        ret = []
        no_r = utils.remove_arg("-r", self.args)
        r_flag = False
        if len(no_r)<len(self.args):
            r_flag = True
        for arg in no_r:
            try:
                ret.append(create_path_obj(arg).resolve())
            except FileNotFoundError:
                self._log_error(f"Cannot remove '{arg}': no such file or directory")

        return ret, r_flag

    def history(self):
        line = self.name
        no_r = utils.remove_arg("-r", self.args)
        line+=get_resolved_line(no_r)

        utils.write_history(line)

    def execute(self):
        args, r_flag = self._parse_args()
        home = os.getenv("HOME")+"/"
        @handlers.handle_all_default
        def remove(path: Path):

            if path == cst.TRASH_PATH:
                self._log_error(f"Unable to remove '{path}' as it is a TRASH")
                return

            if Path.cwd().is_relative_to(path):
                self._log_error(f"Unable to remove '{path}': it is a parent directory")
                return
            no_home = str(path).replace(home, "")
            parent = Path(no_home).parent
            if parent!=Path("/"):
                to_move = Path(cst.TRASH_PATH) / parent

            else:
                to_move = Path(cst.TRASH_PATH)

            if path.is_dir():
                if not r_flag and any(path.iterdir()):
                    self._log_error(f"-r option was not specified: '{path}' is ignored")
                    return

                perm = input(f"Do you want to remove '{path}'? [y/n] ")
                if perm.lower() == "y":
                    shutil.move(path, to_move)
                else:
                    self.logger.warning(f"'{path}' was not removed: user declined operation")
                return

            else:
                shutil.move(path, to_move)

        for arg in args:
            remove(arg)

    def undo(self):
        home = os.environ.get("HOME")+"/"
        for arg in self.args:
            no_home = str(arg).replace(home, "")
            source = Path(cst.TRASH_PATH) / no_home
            self.logger.info(f"Undoing 'rm {arg}")
            shutil.move(source, arg)


@cmd_register.command("history")
class HistoryCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> int | None:
        if self.args:
            try:
                return int(self.args[0])
            except ValueError:
                self._log_error(f"{self.args[0]} is not an integer")
        return None

    def execute(self):
        n = self._parse_args()
        with open(cst.HISTORY_PATH, "r") as file:
            out = ""
            rev = file.readlines()
            if not n:
                n = len(rev)
            for num, line in enumerate(rev[-n:]):
                out += f"{num+1} {line}"
        return out

@cmd_register.command("undo")
class UndoCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> None:
        return None

    def execute(self):
        cur_frame = inspect.currentframe()
        f_back = cur_frame.f_back
        while not getattr(f_back.f_locals["self"], 'cmd_map', None):
            f_back = f_back.f_back

        caller = f_back.f_back.f_locals["self"]

        undoable = list(
            filter(
                lambda x: bool(
                    getattr(caller.cmd_map[x].cmd, "undo", None)
                ), caller.cmd_map.keys()
            )
        )

        with open(cst.HISTORY_PATH, "r") as file:
            history = file.readlines()
            history_rev = history[::-1]
        num_to_delete = None
        for num, hist in enumerate(history_rev):
            hist = hist[:-1]
            name = hist.split(" ")[0]
            if name in undoable:
                try:
                    args = caller.shlex_split(hist)[1:]
                    cmd = caller.cmd_map[name].cmd(args)
                    cmd.undo()
                    num_to_delete = num
                    break
                except Exception as e:
                    self._log_error(f"{e}: {hist}")
                    continue
        if num_to_delete:
            with open(cst.HISTORY_PATH, "w") as file:
                for line in history_rev[:num_to_delete]+history_rev[num_to_delete+1:]:
                    file.write(line)
