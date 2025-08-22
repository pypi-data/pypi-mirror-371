## MCPLoader

MCPLoader is a small helper module that lets you define and consume multiple MCP servers (stdio, SSE, or Streamable HTTP) from a JSON configuration. It uses `pydantic-ai` MCP clients and validates configuration with Pydantic models.

## Features
- **HTTP (SSE / Streamable HTTP)** and **STDIO** server types
- Configuration validation with **Pydantic**
- Multiple MCP servers from a single JSON file
- Simple Python API: pass a config path, get ready-to-use server clients

## Installation
Use it as a module inside your own codebase. Required dependencies:

```bash
pip install mcploader
```

or

```bash
uv add mcploader
```

## Quick start
```python
from mcploader import MCPServerManager

# Provide your configuration file path (e.g., config/http.json or data/mcp/http.json)
manager = MCPServerManager("config/http.json")

servers = manager.servers # serialized list of MCPServer

from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', toolsets=servers)

async def main():
    async with agent:
        await agent.run('Ask something here...')

import asyncio

if __name__ == '__main__':
    asyncio.run(main())
```

## Configuration
Configuration is a JSON object with a root key `mcpServers`. Each key under `mcpServers` is a server name; the value is its configuration.

### General schema
```json
{
  "mcpServers": {
    "<serverName>": { ... }
  }
}
```

Each server can be one of two forms:
- **STDIO**: `StdioServerParameters`
- **HTTP**: `ServerParameters` (contains a `transport` body)

### HTTP (SSE / Streamable HTTP) example
```json
{
  "mcpServers": {
    "server1": {
      "transport": {
        "type": "streamable-http", // or "sse"
        "url": "http://127.0.0.1:8000/mcp",
        "headers": {
          "Authorization": "Bearer your-token-here",
          "Content-Type": "application/json",
          "User-Agent": "Claude-Desktop/1.0",
          "X-API-Version": "v1"
        },
        "timeout": 30000,
        "readTimeout": 300000,
        "maxRetries": 5
      }
    }
  }
}
```

`type` is normalized to lowercase and must be one of:
- `sse`
- `streamable-http`

### STDIO example
```json
{
  "mcpServers": {
    "server1": {
      "command": "deno",
      "args": ["run", "-N", "-R=node_modules", "-W=node_modules", "--node-modules-dir=auto", "jsr:@pydantic/mcp-run-python", "stdio"],
      "env": { "OPENAI_API_KEY": "..." },
      "cwd": "/usr/path/to",
      "timeout": 10,
      "readTimeout": 300,
      "maxRetries": 3
    }
  }
}
```

### Fields and types (summary)
- **HTTP (ServerParameters.transport: ServerBody)**
  - **type**: `"sse" | "streamable-http"`
  - **url**: a valid URL
  - **headers**: `dict[str, str]` (optional)
  - **timeout**: request timeout in ms (default 30000)
  - **readTimeout**: read timeout in ms (default 300000)
  - **maxRetries**: retry count (default 5)
- **STDIO (StdioServerParameters)**
  - **command**: command to execute (e.g., `deno`, `python`)
  - **args**: command arguments (list)
  - **env**: environment variables (key/value)
  - **cwd**: working directory (optional)
  - **timeout**: timeout in seconds (default 30)
  - **readTimeout**: read timeout in seconds (default 300)
  - **maxRetries**: retry count (default 1)

> Note: `ServerParameters.server_type` defaults to `"http"`, `StdioServerParameters.server_type` defaults to `"io"`. These are used internally to select the proper client.

## Folder layout
This repository includes sample configurations under `data/`.

- `data/http.json`: Streamable HTTP example
- `data/sse.json`: SSE example
- `data/stdio.json`: STDIO example

- **Passing paths**: Provide the absolute/relative path directly to `MCPServerManager`, e.g., `MCPServerManager("data/mcp/http.json")`.
- **Schema**: JSON files under `data/` use the same schema; the root must have `mcpServers`, each key defining a server.
- **Environment variants**: You can create `data/mcp/prod/http.json`, `data/mcp/dev/http.json`, etc., and select the appropriate file at runtime.

## API surface
- **`MCPServerManager(config_path: str)`**: Reads the JSON config and validates it with `ServerConfig`.
- **`MCPServerManager.servers -> list[MCPServer]`**: On first access, creates MCP clients (`MCPServerSSE`, `MCPServerStreamableHTTP`, `MCPServerStdio`) according to the config and caches them.

Feel free to reach me from [contact@tomris.dev](mailto:contact@tomris.dev) or my [GitHub](https://github.com/fswair) address.