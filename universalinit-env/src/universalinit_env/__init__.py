"""
UniversalInit Environment Package

A package for mapping environment variables between different frameworks and a common format.
"""

from .envmapper import *

__version__ = "0.1.6"
__all__ = [
    "get_template_path",
    "parse_template_file", 
    "map_common_to_framework",
    "map_framework_to_common",
    "get_supported_frameworks",
    "apply_wildcard_mapping",
]
