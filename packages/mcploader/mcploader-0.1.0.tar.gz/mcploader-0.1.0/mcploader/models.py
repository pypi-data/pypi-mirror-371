from typing import Any, Literal

from pydantic import BaseModel, HttpUrl, model_validator


class StdioServerParameters(BaseModel):
    """
    A model representing a server that handles standard input/output streams.
    """

    command: str
    args: list[str] = []
    env: dict[str, Any] = {}
    cwd: str | None = None
    timeout: int = 30
    readTimeout: int = 300
    maxRetries: int = 1
    server_type: Literal["http", "io"] = "io"


class ServerBody(BaseModel):
    """
    A model representing a server that handles Server-Sent Events (SSE).
    """

    url: HttpUrl
    type: Literal["sse", "streamable-http"]
    headers: dict[str, str] = {}
    timeout: int = 30000
    readTimeout: int = 300000
    maxRetries: int = 5

    @model_validator(mode="before")
    def validate_transport(cls, values: dict) -> dict:
        values["type"] = values["type"].lower().strip()
        return values

    @property
    def is_sse(self) -> bool:
        return self.type == "sse"

    @property
    def is_streamable_http(self) -> bool:
        return self.type == "streamable-http"


class ServerParameters(BaseModel):
    """
    A model representing a server that handles Server-Sent Events (SSE).
    """

    transport: ServerBody
    server_type: Literal["http", "stdio"] = "http"


class ServerConfig(BaseModel):
    """
    A model representing standard input/output streams.
    """

    mcpServers: dict[str, StdioServerParameters | ServerParameters] = {}
