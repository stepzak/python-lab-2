"""Default commands: ls, cat, cd, cp, mv, rm, grep, history, undo, exit"""
import grp
import inspect
import os
import pwd
import re
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

@cmd_register.command("ls", flags = ["-l"])
class LsCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[list[Path], dict[str, bool]]:
        flags = self.parse_flags()
        ret = []
        for arg in self.args:
            ret.append(create_path_obj(arg, must_exist=False))
        if not ret:
            ret.append(create_path_obj("."))
        return ret, flags

    def execute(self):
        paths, flags = self._parse_args()
        out = ""
        l_flag = flags["-l"]
        @handlers.handle_all_default
        def file_info(item: Path):
            output = ""
            name = item.name
            if item.name.startswith("."):
                return ''
            if str(item).find(" ")!=-1:
                name = f'"{name}"'

            if l_flag:
                stat_info = item.stat()

                permissions = stat.filemode(stat_info.st_mode)
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
                output += f"{permissions} {stat_info.st_nlink:>2} {owner} {group} {stat_info.st_size:>8} {time.strftime('%b %d %H:%M', time.gmtime(stat_info.st_mtime))} {name} \n"

            else:
                output+=f"{name} "

            return output


        @handlers.handle_all_default
        def list_dir(path: Path):
            output = ""
            col = utils.get_terminal_dimensions()[0]
            len_counter = 0
            if path.is_file():
                return file_info(path)

            if len(paths)>1:
                output = str(path) + ":\n"
            path_iter = path.iterdir()

            for item in path_iter:
                add = file_info(item)
                if not l_flag:
                    len_counter += len(add)
                    if len_counter > col:
                        len_counter = len(add)
                        add = "\n" + add
                output += add

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

    def _parse_args(self) -> list[Path]:
        if len(self.args)==0:
            return []
        ret = []
        for arg in self.args:
            ret.append(create_path_obj(arg, must_exist=False))
        return ret

    def execute(self):
        paths = self._parse_args()
        output = ""
        if not paths:
            self._log_error("too few arguments")
            return None

        @handlers.handle_all_default
        def read_file(path: Path):
            if path.is_dir():
                msg = f"{path}: is is a directory"
                self._log_error(msg)
                return ''
            elif path.is_file():
                try:
                    with open(path, "r", encoding='utf-8') as file:
                        return file.read()+"\n"
                except Exception as e:
                    print(e)
                    self._log_error(f"unable to read {path}")

            return ''

        for arg in paths:
            output += read_file(arg)
        return output

@cmd_register.command("cp", flags = ["-r"])
class CopyCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[list[Path], Path, dict[str, bool]]:
        flags = self.parse_flags()
        args = self.args
        if len(args)<2:
            self._log_error("too few arguments")
            print("'cp --help' to get more info")
        source_dirs = [utils.create_path_obj(o, must_exist=False) for o in args[:-1]]
        to_dir = utils.create_path_obj(args[-1], must_exist=False).expanduser()

        return source_dirs, to_dir, flags

    def execute(self):
        source_dirs, to_dir, flags = self._parse_args()

        r = flags["-r"]

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
        to_dir = utils.create_path_obj(args[-1], must_exist=False)

        return source_dirs, to_dir


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

        @handlers.handle_all_default
        def undo_(arg: str):
            move_from = source / Path(arg).name
            shutil.move(move_from, arg)

        for p in self.args:
            undo_(p)


@cmd_register.command("rm", flags = ["-r"])
class RemoveCommand(cmds.UndoableCommand):
    def _parse_args(self) -> tuple[list[Path], dict[str, bool]]:
        ret = []
        flags = self.parse_flags()
        for arg in self.args:
            try:
                ret.append(create_path_obj(arg).resolve())
            except FileNotFoundError:
                self._log_error(f"Cannot remove '{arg}': no such file or directory")

        return ret, flags

    def history(self):
        line = self.name
        no_r = utils.remove_arg("-r", self.args)
        line+=get_resolved_line(no_r)

        utils.write_history(line)

    def execute(self):
        args, flags = self._parse_args()
        r_flag = flags["-r"]
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
            if str(parent)[0]=="/":
                parent = Path(str(parent)[1:])
            to_move = Path(cst.TRASH_PATH) / parent
            if not to_move.exists():
                to_move.mkdir(parents=True)

            if path.is_dir():
                if not r_flag and any(path.iterdir()):
                    self._log_error(f"-r option was not specified: '{path}' is ignored")
                    return

                perm = input(f"Do you want to remove '{path}'? [y/n] ")
                if perm.lower() == "y":
                    if not (to_move / path.name).exists():
                        shutil.move(path, to_move)
                    else:
                        shutil.rmtree(to_move)
                        shutil.move(path, to_move)
                else:
                    self.logger.warning(f"'{path}' was not removed: user declined operation")
                return

            else:
                if not (to_move / path.name).exists():
                    shutil.move(path, to_move / path.name)
                else:
                    (to_move/path.name).unlink()
                    shutil.move(path, to_move / path.name)

        for arg in args:
            remove(arg)

    def undo(self):
        home = os.environ.get("HOME")+"/"

        @handlers.handle_all_default
        def undo_(arg: str):
            no_home = str(arg).replace(home, "")
            source = Path(cst.TRASH_PATH) / no_home
            self.logger.info(f"Undoing 'rm {arg}")
            shutil.move(source, arg)

        for p in self.args:
            undo_(p)


@cmd_register.command("grep", flags = ["-i", "-r", "-ir"])
class GrepCommand(cmds.ExecutableCommand):
    def _parse_args(self):
        flags = self.parse_flags()
        if len(self.args)<2:
            self._log_error("too few arguments")
            return None
        f = create_path_obj(self.args[-1])
        if flags["-ir"]:
            flags["-i"] = flags["-r"] = True
        return f, self.args[0], flags

    def execute(self):
        path_arg, regexp, flags = self._parse_args()
        flags_re = 0
        if flags["-i"]:
            flags_re |= re.IGNORECASE
        try:
            compiled = re.compile(regexp, flags_re)
        except re.PatternError:
            self._log_error(f"Invalid regular expression '{regexp}'")
        @handlers.handle_all_default
        def grep(path: Path):
            out = ""
            if path.is_dir():
                if not flags["-r"]:
                    self._log_error(f"'-r' flag was not specified: '{path}' is ignored")
                    return None
                for p in path.iterdir():
                    out+=grep(p)
            elif path.is_file():
                with open(path, "r", encoding='utf-8') as f:
                    for n, line in enumerate(f.readlines(), start = 1):
                        match_found = bool(compiled.search(line))
                        if match_found:
                            line = line.rstrip('\n\r')
                            out+=f"{str(path)}\t {n} {line}\n"
            return out
        output = grep(path_arg)
        return output

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
        with open(cst.HISTORY_PATH, "r", encoding='utf-8') as file:
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

        with open(cst.HISTORY_PATH, "r", encoding='utf-8') as file:
            history = file.readlines()
            history_rev = history[::-1]
        num_to_delete = None
        for num, hist in enumerate(history_rev):
            hist = hist[:-1]
            name = hist.split(" ")[0]
            if name in undoable:
                try:
                    args = caller.shlex_split(hist)[1:]
                    if "--help" in args:
                        continue
                    cmd = caller.cmd_map[name].cmd(args)
                    cmd.undo()
                    num_to_delete = num
                    break
                except Exception as e:
                    self._log_error(f"{e}: {hist}")
                    continue
        if num_to_delete:
            with open(cst.HISTORY_PATH, "w", encoding='utf-8') as file:
                for line in history_rev[:num_to_delete]+history_rev[num_to_delete+1:]:
                    file.write(line)

@cmd_register.command("exit")
class ExitCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> int | None:
        if not self.args:
            return 0
        try:
            return int(self.args[0])
        except ValueError:
            self._log_error(f"{self.args[0]} is not an integer")
            return None

    def execute(self):
        code = self._parse_args()
        if code is not None:
            shutil.rmtree(cst.TRASH_PATH)
            cst.TRASH_PATH.mkdir(parents=True, exist_ok=True)


            return exit(code)
