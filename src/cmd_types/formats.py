from dataclasses import dataclass

@dataclass
class Attribute:
    """
    Attribute dataclass to navigate in some object
    """
    attr_name: str
    """Name of attribute. Can separate with '.' for more deep attributes"""

    attr_getters: list[str | int]
    """Getters for attribute. Now only supported getters for the deepest attribute. Calls '__getitem__' methods of the latest attribute"""

@dataclass
class ErrFormat:
    """
    Formatter for error string
    """
    format_str: str
    """String to format that will support '.format' method"""

    attrs: list[Attribute]
    """List of attributes to format string with"""

    errcode: int = 1
    """Error code"""
