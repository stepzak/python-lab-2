from dataclasses import dataclass

@dataclass
class Attribute:
    attr_name: str
    attr_getters: list[str | int]

@dataclass
class ErrFormat:
    format_str: str
    attrs: list[Attribute]
