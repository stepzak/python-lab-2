from dataclasses import dataclass

from src.cmd_types.commands import ExecutableCommand


@dataclass
class CommandMetadata:
    name: str | None
    plugin_name: str | None
    plugin_author: str | None
    plugin_version: str | None
    cmd: type[ExecutableCommand]
