"""
This package is a small helper module that lets you define and consume multiple MCP servers (stdio, SSE, or Streamable HTTP) from a JSON configuration. It uses `pydantic-ai` MCP clients and validates configuration with Pydantic models.
"""

from .utils import MCPServerManager

__all__ = ["MCPServerManager"]

__version__ = "0.1.0"
