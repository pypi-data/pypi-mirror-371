"""Agentic Blocks - Building blocks for agentic systems."""

from .mcp_client import MCPClient, MCPEndpointError
from .messages import Messages

# Get version from package metadata
try:
    from importlib.metadata import version
    __version__ = version("agentic-blocks")
except Exception:
    __version__ = "unknown"

__all__ = ["MCPClient", "MCPEndpointError", "Messages"]