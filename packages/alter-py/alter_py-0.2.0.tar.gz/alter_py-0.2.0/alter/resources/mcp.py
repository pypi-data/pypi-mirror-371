"""MCP server resource implementation."""

from typing import Any, Dict, List, Optional
from .._types import NOT_GIVEN, NotGiven, RequestOptions
from .._models import BaseModel
from ._base import BaseResource, AsyncBaseResource

__all__ = ["MCPServers", "AsyncMCPServers", "MCPServer", "MCPTool"]


class MCPServer(BaseModel):
    """Unified response model for any MCP server type (for SDK)."""
    id: str
    name: str
    server_type: str  # "external" or "platform"
    status: str


class MCPTool(BaseModel):
    """MCP tool definition model."""
    name: str
    description: str
    parameters: Dict[str, Any]


class MCPServers(BaseResource):
    """MCP servers resource for sync client."""
    
    def list(
        self,
        *,
        options: Optional[RequestOptions] = None,
    ) -> List[MCPServer]:
        """List accessible MCP servers."""
        return self._request(
            "GET",
            "/mcp/servers",
            cast_to=List[MCPServer],
            options=options,
        )
    
    def get_tools(
        self,
        server_id: str,
        *,
        options: Optional[RequestOptions] = None,
    ) -> List[MCPTool]:
        """Get tools from an MCP server."""
        return self._request(
            "GET",
            f"/mcp/servers/{server_id}/tools",
            cast_to=List[MCPTool],
            options=options,
        )
    
    def execute_tool(
        self,
        server_id: str,
        tool_name: str,
        input: Dict[str, Any],
        *,
        options: Optional[RequestOptions] = None,
    ) -> Dict[str, Any]:
        """Execute a tool on an MCP server."""
        return self._request(
            "POST",
            f"/mcp/servers/{server_id}/tools/{tool_name}/execute",
            cast_to=Dict[str, Any],
            body={"inputs": input},
            options=options,
        )


class AsyncMCPServers(AsyncBaseResource):
    """MCP servers resource for async client."""
    
    async def list(
        self,
        *,
        options: Optional[RequestOptions] = None,
    ) -> List[MCPServer]:
        """List accessible MCP servers."""
        return await self._request(
            "GET",
            "/mcp/servers",
            cast_to=List[MCPServer],
            options=options,
        )
    
    async def get_tools(
        self,
        server_id: str,
        *,
        options: Optional[RequestOptions] = None,
    ) -> List[MCPTool]:
        """Get tools from an MCP server.""" 
        return await self._request(
            "GET",
            f"/mcp/servers/{server_id}/tools",
            cast_to=List[MCPTool],
            options=options,
        )
    
    async def execute_tool(
        self,
        server_id: str,
        tool_name: str,
        input: Dict[str, Any],
        *,
        options: Optional[RequestOptions] = None,
    ) -> Dict[str, Any]:
        """Execute a tool on an MCP server."""
        return await self._request(
            "POST",
            f"/mcp/servers/{server_id}/tools/{tool_name}/execute",
            cast_to=Dict[str, Any],
            body={"inputs": input},
            options=options,
        )