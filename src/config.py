"""Configuration settings for the MCP agent."""

import os
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""

    name: str
    transport: str
    url: str
    selected_tools: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by MultiServerMCPClient."""
        return {
            "transport": self.transport,
            "url": self.url,
        }


@dataclass
class AgentConfig:
    """Main configuration for the agent."""

    model: str = "openai:gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create config from environment variables."""
        return cls(
            model=os.getenv("AGENT_MODEL", "openai:gpt-4o"),
            temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "2000")),
        )


# Default MCP server configurations
DEFAULT_MCP_SERVERS = {
    "rag": MCPServerConfig(
        name="rag",
        transport="sse",
        url="https://rshp-mcp.fly.dev/mcp",
        selected_tools=["retrieve_documents"],  # Only use specific tools
    )
}

# Default agent configuration
DEFAULT_AGENT_CONFIG = AgentConfig()
