"""
Email Assistant Agent with MCP Integration

A modular LangGraph agent that integrates with Model Context Protocol (MCP) servers
for enhanced document retrieval and email assistance capabilities.

Main Components:
- agent.py: Main agent creation and entry point
- config.py: Configuration management for servers and agent settings
- prompts.py: System prompts and templates
- tools.py: MCP tools management and integration
- graph.py: Advanced LangGraph workflows (optional)

Quick Start:
    from src.agent import agent

    # The agent is already configured and ready to use
    response = agent.invoke({"messages": [{"role": "user", "content": "Help me find information about X"}]})

Advanced Usage:
    from src.agent import create_agent_with_mcp_tools
    from src.config import MCPServerConfig

    # Create custom agent
    custom_agent = await create_agent_with_mcp_tools(
        prompt_name="rag_assistant",
        selected_tools=["retrieve_documents", "search_web"]
    )
"""

from .agent import agent, create_agent_with_mcp_tools
from .config import DEFAULT_AGENT_CONFIG, AgentConfig, MCPServerConfig
from .prompts import PROMPT_REGISTRY, get_prompt
from .tools import configure_mcp_servers, get_mcp_tools, list_mcp_tools

__version__ = "0.1.0"
__all__ = [
    "agent",
    "create_agent_with_mcp_tools",
    "AgentConfig",
    "MCPServerConfig",
    "DEFAULT_AGENT_CONFIG",
    "get_prompt",
    "PROMPT_REGISTRY",
    "get_mcp_tools",
    "list_mcp_tools",
    "configure_mcp_servers",
]
