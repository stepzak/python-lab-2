import logging

LOG_FILE: str = "/var/log/python-lab-2/shell.log"
FORMAT: str = '[%(asctime)s] %(message)s'
LOGGING_LEVEL: int = logging.DEBUG
FORMAT_LOADER: str = "[ %(asctime)s - %(levelname)s ] %(message)s"

DEFAULT_PWD: str = "~/playground"

PLUGINS_DIR: str = "src.plugins"
PLUGINS_PREFIX: str = "plugin"
STRICT_PLUGIN_LOADING: bool = False