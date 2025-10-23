"""Tools management for MCP integration."""

from typing import Any, Dict, List

from langchain_mcp_adapters.client import MultiServerMCPClient

from .config import DEFAULT_MCP_SERVERS, MCPServerConfig


class MCPToolsManager:
    """Manages MCP server connections and tool filtering."""

    def __init__(self, server_configs: Dict[str, MCPServerConfig] = None):
        """Initialize with server configurations."""
        self.server_configs = server_configs or DEFAULT_MCP_SERVERS
        self._client = None
        self._cached_tools = None

    def _build_client_config(self) -> Dict[str, Dict[str, Any]]:
        """Build configuration dictionary for MultiServerMCPClient."""
        return {name: config.to_dict() for name, config in self.server_configs.items()}

    async def get_client(self) -> MultiServerMCPClient:
        """Get or create MCP client."""
        if self._client is None:
            client_config = self._build_client_config()
            self._client = MultiServerMCPClient(client_config)
        return self._client

    async def get_all_tools(self) -> List[Any]:
        """Get all available tools from MCP servers."""
        if self._cached_tools is None:
            client = await self.get_client()
            self._cached_tools = await client.get_tools()
        return self._cached_tools

    async def get_filtered_tools(self, selected_tools: List[str] = None) -> List[Any]:
        """Get tools filtered by name."""
        all_tools = await self.get_all_tools()

        if not selected_tools:
            # If no specific tools requested, use configured selections
            selected_tools = []
            for config in self.server_configs.values():
                if config.selected_tools:
                    selected_tools.extend(config.selected_tools)

        if not selected_tools:
            # If still no tools specified, return all
            return all_tools

        # Filter tools by name
        filtered_tools = [tool for tool in all_tools if tool.name in selected_tools]

        # Log missing tools
        found_tool_names = {tool.name for tool in filtered_tools}
        missing_tools = set(selected_tools) - found_tool_names
        if missing_tools:
            print(f"Warning: Tools not found: {missing_tools}")
            available_tools = [tool.name for tool in all_tools]
            print(f"Available tools: {available_tools}")

        return filtered_tools

    async def list_available_tools(self) -> Dict[str, str]:
        """Get a dictionary of available tools with their descriptions."""
        all_tools = await self.get_all_tools()
        return {
            tool.name: getattr(tool, "description", "No description available")
            for tool in all_tools
        }

    def add_server(self, name: str, config: MCPServerConfig):
        """Add a new MCP server configuration."""
        self.server_configs[name] = config
        # Clear cached client and tools to force refresh
        self._client = None
        self._cached_tools = None

    def remove_server(self, name: str):
        """Remove an MCP server configuration."""
        if name in self.server_configs:
            del self.server_configs[name]
            # Clear cached client and tools to force refresh
            self._client = None
            self._cached_tools = None


# Global instance for easy access
_tools_manager = MCPToolsManager()


async def get_mcp_tools(selected_tools: List[str] = None) -> List[Any]:
    """Convenience function to get MCP tools."""
    return await _tools_manager.get_filtered_tools(selected_tools)


async def list_mcp_tools() -> Dict[str, str]:
    """Convenience function to list available MCP tools."""
    return await _tools_manager.list_available_tools()


def configure_mcp_servers(server_configs: Dict[str, MCPServerConfig]):
    """Configure MCP servers globally."""
    global _tools_manager
    _tools_manager = MCPToolsManager(server_configs)
