import logging
from pathlib import Path

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
