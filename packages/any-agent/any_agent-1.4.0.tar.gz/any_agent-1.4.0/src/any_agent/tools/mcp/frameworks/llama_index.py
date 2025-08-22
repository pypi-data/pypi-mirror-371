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
    from llama_index.core.tools import (
        FunctionTool as LlamaIndexFunctionTool,  # noqa: TC002
    )
    from llama_index.tools.mcp import BasicMCPClient as LlamaIndexMCPClient
    from llama_index.tools.mcp import McpToolSpec as LlamaIndexMcpToolSpec

    mcp_available = True


class LlamaIndexMCPConnection(_MCPConnection["LlamaIndexFunctionTool"], ABC):
    """Base class for LlamaIndex MCP connections."""

    _client: "LlamaIndexMCPClient | None" = PrivateAttr(default=None)

    @abstractmethod
    async def list_tools(self) -> list["LlamaIndexFunctionTool"]:
        """List tools from the MCP server."""
        if not self._client:
            msg = "MCP client is not set up. Please call `list_tool` from a concrete class."
            raise ValueError(msg)

        allowed_tools = self.mcp_tool.tools
        if allowed_tools is not None:
            allowed_tools = list(allowed_tools)
        mcp_tool_spec = LlamaIndexMcpToolSpec(
            client=self._client,
            allowed_tools=allowed_tools,
        )

        return await mcp_tool_spec.to_tool_list_async()


class LlamaIndexMCPStdioConnection(LlamaIndexMCPConnection):
    mcp_tool: MCPStdio

    async def list_tools(self) -> list["LlamaIndexFunctionTool"]:
        """List tools from the MCP server."""
        kwargs = {}
        if self.mcp_tool.client_session_timeout_seconds:
            kwargs["timeout"] = self.mcp_tool.client_session_timeout_seconds
        self._client = LlamaIndexMCPClient(
            command_or_url=self.mcp_tool.command,
            args=list(self.mcp_tool.args),
            env=self.mcp_tool.env,
            **kwargs,  # type: ignore[arg-type]
        )
        return await super().list_tools()


class LlamaIndexMCPSseConnection(LlamaIndexMCPConnection):
    mcp_tool: MCPSse

    async def list_tools(self) -> list["LlamaIndexFunctionTool"]:
        """List tools from the MCP server."""
        kwargs = {}
        if self.mcp_tool.client_session_timeout_seconds:
            kwargs["timeout"] = self.mcp_tool.client_session_timeout_seconds
        self._client = LlamaIndexMCPClient(
            command_or_url=self.mcp_tool.url,
            **kwargs,  # type: ignore[arg-type]
        )
        return await super().list_tools()


class LlamaIndexMCPStreamableConnection(LlamaIndexMCPConnection):
    mcp_tool: MCPStreamableHttp

    async def list_tools(self) -> list["LlamaIndexFunctionTool"]:
        """List tools from the MCP server."""
        kwargs = {}
        if self.mcp_tool.client_session_timeout_seconds:
            kwargs["timeout"] = self.mcp_tool.client_session_timeout_seconds
        self._client = LlamaIndexMCPClient(
            command_or_url=self.mcp_tool.url,
            **kwargs,  # type: ignore[arg-type]
        )
        return await super().list_tools()


class LlamaIndexMCPServerBase(_MCPServerBase["LlamaIndexFunctionTool"], ABC):
    framework: Literal[AgentFramework.LLAMA_INDEX] = AgentFramework.LLAMA_INDEX
    tools: Sequence["LlamaIndexFunctionTool"] = Field(default_factory=list)

    def _check_dependencies(self) -> None:
        """Check if the required dependencies for the MCP server are available."""
        self.libraries = "any-agent[mcp,llama_index]"
        self.mcp_available = mcp_available
        super()._check_dependencies()


class LlamaIndexMCPServerStdio(LlamaIndexMCPServerBase):
    mcp_tool: MCPStdio

    async def _setup_tools(
        self, mcp_connection: _MCPConnection["LlamaIndexFunctionTool"] | None = None
    ) -> None:
        mcp_connection = mcp_connection or LlamaIndexMCPStdioConnection(
            mcp_tool=self.mcp_tool
        )
        await super()._setup_tools(mcp_connection)


class LlamaIndexMCPServerSse(LlamaIndexMCPServerBase):
    mcp_tool: MCPSse

    async def _setup_tools(
        self, mcp_connection: _MCPConnection["LlamaIndexFunctionTool"] | None = None
    ) -> None:
        mcp_connection = mcp_connection or LlamaIndexMCPSseConnection(
            mcp_tool=self.mcp_tool
        )
        await super()._setup_tools(mcp_connection)


class LlamaIndexMCPServerStreamableHttp(LlamaIndexMCPServerBase):
    mcp_tool: MCPStreamableHttp

    async def _setup_tools(
        self, mcp_connection: _MCPConnection["LlamaIndexFunctionTool"] | None = None
    ) -> None:
        mcp_connection = mcp_connection or LlamaIndexMCPStreamableConnection(
            mcp_tool=self.mcp_tool
        )
        await super()._setup_tools(mcp_connection)


LlamaIndexMCPServer = (
    LlamaIndexMCPServerStdio
    | LlamaIndexMCPServerSse
    | LlamaIndexMCPServerStreamableHttp
)
