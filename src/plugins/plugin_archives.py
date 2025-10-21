import shutil
from pathlib import Path
from typing import Literal
import src.decorators.commands_register as cmd_register
import src.decorators.handlers as handlers
from src.cmd_types.commands import ExecutableCommand
from src.extra.utils import create_path_obj
import src.constants as cst

__author__ = "default"
__version__ = "1.0.0"


class UnpackCommand(ExecutableCommand):

    archive_type: str

    def _parse_args(self) -> tuple[str, str]:
        return self.args[0], self.args[1]

    @handlers.handle_all_default
    def execute(self):
        if len(self.args)!=2:
            self._log_error(f"{self.name} command requires exactly 2 arguments. Given: {len(self.args)}")
            return None

        ext = "."+cst.TYPE_EXTENSION_ENUM[self.archive_type]

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
            self._log_error(f"not a directory: {source}")

    @handlers.handle_all_default
    def execute(self):

        if len(self.args)!=2:
            self._log_error(f"{self.name} command requires exactly 2 arguments. Given: {len(self.args)}")
            return None

        ext = cst.TYPE_EXTENSION_ENUM[self.archive_type]
        if not self.args[1].endswith(f".{ext}"):
            self._log_error(f"{self.name} command requires .{ext} extension. Given: {self.args[1]}")
            return None

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
