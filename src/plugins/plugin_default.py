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
from src.cmd_types.output import CommandOutput
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
        out = CommandOutput()
        l_flag = flags["-l"]
        @handlers.handle_all_default
        def file_info(item: Path):
            output = ""
            name = item.name
            if item.name.startswith("."):
                return CommandOutput()
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

            return CommandOutput(
                stdout = output
            )


        @handlers.handle_all_default
        def list_dir(path: Path):
            output = CommandOutput()
            col = utils.get_terminal_dimensions()[0]
            len_counter = 0
            if path.is_file():
                return file_info(path)
            next_line = 0
            if len(paths)>1:
                output.stdout = str(path) + ":\n"
                next_line = 1
            path_iter = path.iterdir()

            for item in path_iter:
                add = file_info(item)
                add_stdout = add.stdout
                if not l_flag:
                    len_counter += len(add_stdout)
                    if len_counter > col:
                        len_counter = len(add_stdout)
                        add.stdout = "\n" + add_stdout
                output += add

            output.stdout+=next_line*"\n\n"
            return output

        for arg in paths:
            add_global = list_dir(arg)
            out+=add_global

        return out

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
            msg = "too many arguments\n"
            return CommandOutput(stderr = msg, errcode = 4)
        if path.is_dir():
            os.chdir(path)
            return CommandOutput()
        elif path.is_file():

            msg = f"{path}: it is a file\n"
            return CommandOutput(stderr = msg, errcode = 2)
        return CommandOutput(stderr = f"not found: {path}", errcode = 2)


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
        output = CommandOutput()
        if not paths:
            msg = "too few arguments\n"
            return CommandOutput(stderr = msg, errcode = 4)

        @handlers.handle_all_default
        def read_file(path: Path):
            if path.is_dir():
                msg = f"{path}: is is a directory\n"
                return CommandOutput(stderr = msg, errcode = 2)
            elif path.is_file():
                try:
                    with open(path, "r", encoding='utf-8') as file:
                        return file.read()+"\n"
                except Exception:
                    return CommandOutput(stderr = f"unable to read {path}\n", errcode = 3)

            raise FileNotFoundError(2, path, str(path))

        for arg in paths:
            output += read_file(arg)
        return output

@cmd_register.command("cp", flags = ["-r"])
class CopyCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> tuple[list[Path], Path, dict[str, bool]]:
        flags = self.parse_flags()
        args = self.args
        source_dirs = [utils.create_path_obj(o, must_exist=False) for o in args[:-1]]
        to_dir = utils.create_path_obj(args[-1], must_exist=False).expanduser()

        return source_dirs, to_dir, flags

    def execute(self):
        if len(self.args) < 2:
            return CommandOutput(stderr = "too few arguments\n", errcode = 4)
        source_dirs, to_dir, flags = self._parse_args()
        out = CommandOutput()
        r = flags["-r"]

        @handlers.handle_all_default
        def copy(source: Path, to: Path):
            if source.is_dir():
                if not r:
                    msg = f"-r option was not specified: '{source}' is ignored\n"
                    return CommandOutput(stderr = msg, errcode = 1)

                if to_dir.resolve().is_relative_to(source_dir.resolve()):
                    msg = f"Unable to copy '{to}' to itself\n"
                    return CommandOutput(stderr = msg, errcode = 1)
                try:
                    shutil.copytree(source, to, dirs_exist_ok=True)
                except shutil.Error as e:
                    for arg in e.args[0]:
                        msg = f"{arg[0]}: {arg[2]}\n"
                        return CommandOutput(stderr = msg, errcode = 1)
                return None

            shutil.copy2(source, to)
            return None

        for source_dir in source_dirs:
            res = copy(source_dir, to_dir)
            if res:
                out += res
        return out


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
        out = CommandOutput()
        for source_dir in source_dirs:
            if to_dir.resolve().is_relative_to(source_dir.resolve()):
                out.stderr += f"unable to move '{source_dir}' to itself\n"
                out.errcode = 2
                continue
            shutil.move(source_dir, to_dir)
        return out

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
                ret.append(create_path_obj(arg, must_exist=False).resolve())
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
        out = CommandOutput()
        home = os.getenv("HOME")+"/"
        @handlers.handle_all_default
        def remove(path: Path):

            if path == cst.TRASH_PATH:
                msg = f"unable to remove '{path}' as it is a TRASH\n"
                return CommandOutput(stderr = msg, errcode = 2)

            if Path.cwd().is_relative_to(path):
                msg = f"unable to remove '{path}': it is a parent directory\n"
                return CommandOutput(stderr = msg, errcode = 2)
            no_home = str(path).replace(home, "")
            parent = Path(no_home).parent
            if str(parent)[0]=="/":
                parent = Path(str(parent)[1:])
            to_move = Path(cst.TRASH_PATH) / parent
            if not to_move.exists():
                to_move.mkdir(parents=True)

            if path.is_dir():
                if not r_flag and any(path.iterdir()):
                    msg = f"-r option was not specified: '{path}' is ignored\n"
                    return CommandOutput(stderr = msg, errcode = 2)

                perm = input(f"Do you want to remove '{path}'? [y/n] ")
                if perm.lower() == "y":
                    if not (to_move / path.name).exists():
                        shutil.move(path, to_move)
                    else:
                        shutil.rmtree(to_move)
                        shutil.move(path, to_move)
                else:
                    self.logger.warning(f"'{path}' was not removed: user declined operation")
                return CommandOutput()

            else:
                if not (to_move / path.name).exists():
                    shutil.move(path, to_move / path.name)
                else:
                    (to_move/path.name).unlink()
                    shutil.move(path, to_move / path.name)

        for arg in args:
            res = remove(arg)
            if res:
                out += res
        return out


    def undo(self):
        home = os.environ.get("HOME")+"/"

        @handlers.handle_all_default
        def undo_(arg: str):
            no_home = str(arg).replace(home, "")
            source = Path(cst.TRASH_PATH) / no_home
            self.logger.info(f"undoing 'rm {arg}")
            shutil.move(source, arg)

        for p in self.args:
            undo_(p)


@cmd_register.command("grep", flags = ["-i", "-r", "-ir"])
class GrepCommand(cmds.ExecutableCommand):
    def _parse_args(self):
        flags = self.parse_flags()
        f = create_path_obj(self.args[-1], must_exist=False)
        if flags["-ir"]:
            flags["-i"] = flags["-r"] = True
        return f, self.args[0], flags

    def execute(self):
        if len(self.args) < 2:
            msg = "too few arguments"
            return CommandOutput(stderr = msg, errcode = 4)
        path_arg, regexp, flags = self._parse_args()
        flags_re = 0
        if flags["-i"]:
            flags_re |= re.IGNORECASE
        try:
            compiled = re.compile(regexp, flags_re)
        except re.PatternError:
            msg = f"invalid regular expression '{regexp}'"
            return CommandOutput(stderr = msg, errcode = 5)
        @handlers.handle_all_default
        def grep(path: Path) -> CommandOutput:
            out = CommandOutput()
            if path.is_dir():
                if not flags["-r"]:
                    msg = f"'-r' flag was not specified: '{path}' is ignored"
                    return CommandOutput(stderr = msg, errcode = 2)
                for p in path.iterdir():
                    out+=grep(p)
            elif path.is_file():
                with open(path, "r", encoding='utf-8') as f:
                    for n, line in enumerate(f.readlines(), start = 1):
                        match_found = bool(compiled.search(line))
                        if match_found:
                            line = line.rstrip('\n\r')
                            out.stdout+=f"{str(path)}\t {n} {line}\n"
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
        return CommandOutput(stdout = out)

@cmd_register.command("undo")
class UndoCommand(cmds.ExecutableCommand):
    def _parse_args(self) -> None:
        return None

    def execute(self):
        cur_frame = inspect.currentframe()
        f_back = cur_frame.f_back
        while not getattr(f_back.f_locals["self"], 'cmd_map', None):
            f_back = f_back.f_back
        out = CommandOutput()
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
                    out.stderr +=f"{e}: {hist}\n"
                    continue
        if num_to_delete:
            with open(cst.HISTORY_PATH, "w", encoding='utf-8') as file:
                for line in history_rev[:num_to_delete]+history_rev[num_to_delete+1:]:
                    file.write(line)
        return out

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
