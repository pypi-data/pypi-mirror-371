"""Magique AI toolsets package."""

__version__ = "0.5.3"

from .remote import connect_remote
from .utils.toolset import ToolSet, tool, run_toolsets

__all__ = ["connect_remote", "ToolSet", "tool", "run_toolsets"]
