from dataclasses import dataclass
from types import ModuleType
from typing import Any


@dataclass
class PluginMetadata:
    module: ModuleType
    author: Any
    version: Any
