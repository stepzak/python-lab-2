import logging
from pathlib import Path
from src.cmd_types.formats import ErrFormat, Attribute

LOG_FILE: str = "/var/log/python-lab-2/shell.log"
FORMAT: str = '[%(asctime)s] %(message)s'
LOGGING_LEVEL: int = logging.DEBUG
FORMAT_LOADER: str = "[ %(asctime)s - %(levelname)s ] %(message)s"

DEFAULT_PWD: Path = Path("~/playground").expanduser()

PLUGINS_DIR: str = "src.plugins"
PLUGINS_PREFIX: str = "plugin"
STRICT_PLUGIN_LOADING: bool = False

HISTORY_PATH: Path = Path(DEFAULT_PWD) / ".history"
TRASH_PATH: Path = Path(DEFAULT_PWD) / ".trash"

TYPE_EXTENSION_ENUM: dict[str, str] = {
            "gztar": "tar.gz",
            "zip": "zip"
        }

ERROR_HANDLERS_MESSAGES_FORMATS: dict[type[Exception], ErrFormat] = {
    FileNotFoundError: ErrFormat(
        format_str = "{0}: no such file or directory",
        attrs = [
            Attribute("filename", [])
        ]
    ),
    PermissionError: ErrFormat(
        format_str = "{0}: permission denied",
        attrs = [
            Attribute("filename", [])
        ]
    ),
    UnicodeDecodeError: ErrFormat(
        format_str = "unicode decoding error",
        attrs = []
    )
}
