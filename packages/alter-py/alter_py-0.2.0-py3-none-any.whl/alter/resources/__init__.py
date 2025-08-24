"""Resource classes for the Alter Python client."""

from .health import HealthResource, AsyncHealthResource
from .mcp import MCPServers, AsyncMCPServers

__all__ = [
    "HealthResource",
    "AsyncHealthResource",
    "MCPServers",
    "AsyncMCPServers",
]