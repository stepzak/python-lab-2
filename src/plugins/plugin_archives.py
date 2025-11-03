"""Plugin to work with archives"""
import shutil
from pathlib import Path
from typing import Literal
import src.decorators.commands_register as cmd_register
import src.decorators.handlers as handlers
from src.cmd_types.commands import ExecutableCommand
from src.cmd_types.output import CommandOutput
from src.extra.utils import create_path_obj
import src.constants as cst

__author__ = "default"
__version__ = "1.0.0"

TYPES = tuple(cst.TYPE_EXTENSION_ENUM.keys())

class UnpackCommand(ExecutableCommand):
    """
    Command class to unpack archives
    """
    archive_type: str
    """type of archive"""

    def _parse_args(self) -> tuple[str, str]:
        return self.args[0], self.args[1]

    @handlers.handle_all_default
    def execute(self):
        ext = "." + cst.TYPE_EXTENSION_ENUM[self.archive_type]
        if len(self.args)==1:
            self.args.append(self.args[0][:-len(ext)])
        if len(self.args)!=2:
            self._log_error(f"{self.name} command requires exactly at least 2 arguments. Given: {len(self.args)}")
            return None
        if not self.args[0].endswith(ext):
            self._log_error(f"{self.name} command requires {ext} extension. Given: {self.args[0]}")
            return None
        source = create_path_obj(self.args[0])

        try:
            shutil.unpack_archive(source, self.args[1])
        except shutil.ReadError as e:
            self._log_error(str(e))
        return None


class PackCommand(ExecutableCommand):
    """Command to pack archives"""

    archive_type: Literal["gztar", "zip"]

    def _parse_args(self) -> tuple[str, str]:
        return self.args[0], self.args[1]

    def make_archive(self, source: str | Path, destination: str | Path, archive_type: Literal["gztar", "zip"]):
        source, destination = str(source), str(destination)

        ext = '.'+cst.TYPE_EXTENSION_ENUM[archive_type]

        if destination.endswith(ext):
            destination = destination[:-len(ext)]
        try:
            shutil.make_archive(destination, archive_type, source)
        except NotADirectoryError:
            msg = f"not a directory: {source}"
            return CommandOutput(stderr = msg, errcode = 2)

    @handlers.handle_all_default
    def execute(self):

        ext = "." + cst.TYPE_EXTENSION_ENUM[self.archive_type]
        if len(self.args) == 1:
            self.args.append(self.args[0]+ext)

        if len(self.args)!=2:
            msg = f"{self.name} command requires at leat 1 argument. Given: {len(self.args)}"
            return CommandOutput(stderr = msg, errcode = 2)


        if not self.args[1].endswith(f"{ext}"):
            msg = f"{self.name} command requires {ext} extension. Given: {self.args[1]}"
            return CommandOutput(stderr= msg, errcode=2)

        source = create_path_obj(self.args[0])

        self.make_archive(source, self.args[1], self.archive_type)
        return None


@cmd_register.command("tar")
class TarCommand(PackCommand):
    archive_type = "gztar"


@cmd_register.command("zip")
class ZipCommand(PackCommand):
    archive_type = "zip"


@cmd_register.command("untar")
class UntarCommand(UnpackCommand):
    archive_type = "gztar"


@cmd_register.command("unzip")
class UnzipCommand(UnpackCommand):
    archive_type = "zip"
