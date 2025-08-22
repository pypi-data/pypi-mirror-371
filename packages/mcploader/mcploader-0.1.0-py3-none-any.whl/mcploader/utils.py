import json
import pathlib

from pydantic_ai.mcp import (
    MCPServer,
    MCPServerSSE,
    MCPServerStdio,
    MCPServerStreamableHTTP,
)

from .models import ServerConfig


class MCPServerManager:
    """
    A manager for MCP servers.
    """

    def __init__(self, config_path: str):
        self.mcp_config: dict = json.loads(
            pathlib.Path(config_path).read_text(encoding="utf-8")
        )
        self.server_config = ServerConfig(**self.mcp_config)
        self._mcp_servers: list[MCPServer] = []

    def get_mcp_servers(self) -> list[MCPServer]:
        """
        Returns the MCP servers from the MCP configuration.
        """
        mcp_servers = []
        for name, server in self.server_config.mcpServers.items():
            if server.server_type == "http":
                if server.transport.is_sse:
                    mcp_server = MCPServerSSE(
                        url=server.transport.url._url.unicode_string(),
                        headers=server.transport.headers,
                        timeout=server.transport.timeout,
                        read_timeout=server.transport.readTimeout,
                        max_retries=server.transport.maxRetries,
                        id=name,
                    )

                elif server.transport.is_streamable_http:
                    mcp_server = MCPServerStreamableHTTP(
                        url=server.transport.url._url.unicode_string(),
                        headers=server.transport.headers,
                        timeout=server.transport.timeout,
                        read_timeout=server.transport.readTimeout,
                        max_retries=server.transport.maxRetries,
                        id=name,
                    )

            elif server.server_type == "io":
                mcp_server = MCPServerStdio(
                    command=server.command,
                    timeout=server.timeout,
                    args=server.args,
                    env=server.env,
                    cwd=server.cwd,
                    read_timeout=server.readTimeout,
                    max_retries=server.maxRetries,
                    id=name,
                )
            mcp_servers.append(mcp_server)
        return mcp_servers

    @property
    def servers(self) -> list[MCPServer]:
        """
        Returns the list of MCP servers.
        """
        if not self._mcp_servers:
            self._mcp_servers = self.get_mcp_servers()
        return self._mcp_servers
