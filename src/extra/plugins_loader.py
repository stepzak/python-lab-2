import importlib
import inspect
import logging
import pkgutil
from sys import stdout

import src.constants as cst
from src.cmd_types.commands import ExecutableCommand


class PluginLoader:
    def __init__(self, pkg_dir: str = cst.PLUGINS_DIR, prefix: str = cst.PLUGINS_PREFIX, strict: bool = cst.STRICT_PLUGIN_LOADING):
        self.pkg_dir = pkg_dir
        self.prefix = prefix
        self.logger = logging.Logger(__name__)
        self.commands: dict[str, type[ExecutableCommand]] = {}
        self.strict = strict
        self.__init_logger()

    def __init_logger(self):
        handlers = [
            logging.FileHandler(cst.LOG_FILE, mode="a", encoding="utf-8"),
            logging.StreamHandler(stdout),
        ]
        formatter = logging.Formatter(cst.FORMAT_LOADER)
        for handler in handlers:
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(cst.LOGGING_LEVEL)

    def load_plugins(self):

        plugins_pkg = importlib.import_module(self.pkg_dir)
        for importer, module_name, is_pkg in pkgutil.iter_modules(plugins_pkg.__path__):
            if module_name.startswith(self.prefix + "_") and not is_pkg:
                self._load_module(module_name)

    def warn_or_error(self, *, warn_msg: str = "", exc: Exception = ImportError):
        if not self.strict:
            self.logger.warning(warn_msg)

        else:
            raise exc


    def _load_module(self, module_name: str):
        full_module_name = f"{self.pkg_dir}.{module_name}"
        module = importlib.import_module(full_module_name)

        self.logger.debug(f"Loading module {full_module_name}...")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if issubclass(obj, ExecutableCommand):
                    cmd_name = obj.name
                    if self.commands.get(cmd_name):

                        warn_msg = f"Command {cmd_name} in module {full_module_name} already exists, skipping"

                        exc = ImportError(f"{cmd_name} imported twice", name = module_name, path = full_module_name)

                        self.warn_or_error(warn_msg=warn_msg, exc=exc)

                    elif " " in cmd_name:
                        warn_msg = f"Command {cmd_name} in module {full_module_name} has spaces in it"
                        exc = ImportError(warn_msg, name = module_name, path = full_module_name)
                        warn_msg+=", skipping"

                        self.warn_or_error(warn_msg=warn_msg, exc=exc)

                    else:
                        self.logger.debug(f"Loading command {cmd_name}...")
                        self.commands[cmd_name] = obj
                        self.logger.debug(f"Command {cmd_name} in module {full_module_name} loaded")

        self.logger.debug(f"Loaded module {full_module_name}")