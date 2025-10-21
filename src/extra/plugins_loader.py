import importlib
import inspect
import logging
import pkgutil
import sys
from sys import stdout
from typing import Any

import src.constants as cst
from src.cmd_types.commands import ExecutableCommand, UndoableCommand
from src.cmd_types.meta import CommandMetadata
from src.cmd_types.plugins import PluginMetadata

RESTRICTED = (ExecutableCommand, UndoableCommand)

class PluginLoader:
    def __init__(self, pkg_dir: str = cst.PLUGINS_DIR, prefix: str = cst.PLUGINS_PREFIX, strict: bool = cst.STRICT_PLUGIN_LOADING):
        self.pkg_dir = pkg_dir
        self.prefix = prefix
        self.logger = logging.Logger(__name__)
        self.commands: dict[str, CommandMetadata] = {}
        self.strict = strict
        self.__init_logger()
        self.non_default: dict[str, PluginMetadata] = {}

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
            if module_name.startswith(self.prefix) and not is_pkg:
                self._load_module(module_name)
        for k in self.non_default.keys():
            self._load_module(k, False)

    def warn_or_error(self, *, warn_msg: str = "", exc: Any = ImportError):
        if not self.strict:
            self.logger.warning(warn_msg)

        else:
            raise exc


    def _load_module(self, module_name: str, defaults: bool = True):
        full_module_name = defaults * f'{self.pkg_dir}.' + f"{module_name}"
        if defaults:
            try:
                if full_module_name in sys.modules:
                    module = sys.modules[full_module_name]
                    importlib.reload(module)
                    self.logger.debug(f"Module {module.__name__} already imported: reloading")
                else:
                    module = importlib.import_module(full_module_name)
            except Exception as e:
                self.warn_or_error(warn_msg=f"Failed to load module {full_module_name}: {e}", exc=e)
                return
            author = getattr(module, "__author__", None)
            version = getattr(module, "__version__", None)
            if author != "default" :
                self.non_default[full_module_name] = PluginMetadata(module = module, author = author, version = version)
                return
        else:
            obj_import = self.non_default[full_module_name]
            module = obj_import.module
            author = obj_import.author
            version = obj_import.version
        self.logger.debug(f"Loading {'non-default' if not defaults else 'default'} module {full_module_name}...")
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if issubclass(obj, ExecutableCommand) and obj not in RESTRICTED:
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
                        self.commands[cmd_name] = CommandMetadata(
                            name = cmd_name,
                            plugin_name = module_name,
                            plugin_author=author,
                            plugin_version=version,
                            cmd = obj
                            )
                        self.logger.debug(f"Command {cmd_name} in module {full_module_name} loaded")

        self.logger.debug(f"Loaded module {full_module_name}")
