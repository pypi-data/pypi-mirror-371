"""Agentic Blocks - Building blocks for agentic systems."""

from .mcp_client import MCPClient, MCPEndpointError
from .messages import Messages

__version__ = "0.1.0"

__all__ = ["MCPClient", "MCPEndpointError", "Messages"]