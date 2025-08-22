from abc import ABC, abstractmethod
from collections.abc import Sequence
from contextlib import suppress
from typing import Literal

from pydantic import Field, PrivateAttr

from any_agent.config import AgentFramework, MCPSse, MCPStdio, MCPStreamableHttp
from any_agent.tools.mcp.mcp_connection import _MCPConnection
from any_agent.tools.mcp.mcp_server import _MCPServerBase

mcp_available = False
with suppress(ImportError):
    from mcp import StdioServerParameters
    from smolagents.mcp_client import MCPClient
    from smolagents.tools import Tool as SmolagentsTool  # noqa: TC002

    mcp_available = True


class SmolagentsMCPConnection(_MCPConnection["SmolagentsTool"], ABC):
    """Base class for Smolagents MCP connections."""

    _client: "MCPClient | None" = PrivateAttr(default=None)

    @abstractmethod
    async def list_tools(self) -> list["SmolagentsTool"]:
        """List tools from the MCP server."""
        if not self._client:
            msg = "Tool collection is not set up. Please call `list_tools` from a concrete class."
            raise ValueError(msg)

        tools = self._client.get_tools()
        return self._filter_tools(tools)  # type: ignore[return-value]


class SmolagentsMCPStdioConnection(SmolagentsMCPConnection):
    mcp_tool: MCPStdio

    async def list_tools(self) -> list["SmolagentsTool"]:
        """List tools from the MCP server."""
        server_parameters = StdioServerParameters(
            command=self.mcp_tool.command,
            args=list(self.mcp_tool.args),
            env=self.mcp_tool.env,
        )
        adapter_kwargs = {}
        if self.mcp_tool.client_session_timeout_seconds:
            adapter_kwargs["connect_timeout"] = (
                self.mcp_tool.client_session_timeout_seconds
            )
        self._client = MCPClient(server_parameters, adapter_kwargs=adapter_kwargs)
        return await super().list_tools()


class SmolagentsMCPSseConnection(SmolagentsMCPConnection):
    mcp_tool: MCPSse

    async def list_tools(self) -> list["SmolagentsTool"]:
        """List tools from the MCP server."""
        server_parameters = {"url": self.mcp_tool.url, "transport": "sse"}
        adapter_kwargs = {}
        if self.mcp_tool.client_session_timeout_seconds:
            adapter_kwargs["connect_timeout"] = (
                self.mcp_tool.client_session_timeout_seconds
            )
        self._client = MCPClient(server_parameters, adapter_kwargs=adapter_kwargs)

        return await super().list_tools()


class SmolagentsMCPStreamableHttpConnection(SmolagentsMCPConnection):
    mcp_tool: MCPStreamableHttp

    async def list_tools(self) -> list["SmolagentsTool"]:
        """List tools from the MCP server."""
        server_parameters = {"url": self.mcp_tool.url, "transport": "streamable-http"}
        adapter_kwargs = {}
        if self.mcp_tool.client_session_timeout_seconds:
            adapter_kwargs["connect_timeout"] = (
                self.mcp_tool.client_session_timeout_seconds
            )
        self._client = MCPClient(server_parameters, adapter_kwargs=adapter_kwargs)

        return await super().list_tools()


class SmolagentsMCPServerBase(_MCPServerBase["SmolagentsTool"], ABC):
    framework: Literal[AgentFramework.SMOLAGENTS] = AgentFramework.SMOLAGENTS
    tools: Sequence["SmolagentsTool"] = Field(default_factory=list)

    def _check_dependencies(self) -> None:
        """Check if the required dependencies for the MCP server are available."""
        self.libraries = "any-agent[mcp,smolagents]"
        self.mcp_available = mcp_available
        super()._check_dependencies()


class SmolagentsMCPServerStdio(SmolagentsMCPServerBase):
    mcp_tool: MCPStdio

    async def _setup_tools(
        self, mcp_connection: _MCPConnection["SmolagentsTool"] | None = None
    ) -> None:
        mcp_connection = mcp_connection or SmolagentsMCPStdioConnection(
            mcp_tool=self.mcp_tool
        )
        await super()._setup_tools(mcp_connection)


class SmolagentsMCPServerSse(SmolagentsMCPServerBase):
    mcp_tool: MCPSse

    async def _setup_tools(
        self, mcp_connection: _MCPConnection["SmolagentsTool"] | None = None
    ) -> None:
        mcp_connection = mcp_connection or SmolagentsMCPSseConnection(
            mcp_tool=self.mcp_tool
        )
        await super()._setup_tools(mcp_connection)


class SmolagentsMCPServerStreamableHttp(SmolagentsMCPServerBase):
    mcp_tool: MCPStreamableHttp

    async def _setup_tools(
        self, mcp_connection: _MCPConnection["SmolagentsTool"] | None = None
    ) -> None:
        mcp_connection = mcp_connection or SmolagentsMCPStreamableHttpConnection(
            mcp_tool=self.mcp_tool
        )
        await super()._setup_tools(mcp_connection)


SmolagentsMCPServer = (
    SmolagentsMCPServerStdio
    | SmolagentsMCPServerSse
    | SmolagentsMCPServerStreamableHttp
)
