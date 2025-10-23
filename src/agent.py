"""Main agent module with clean, modular structure."""

import asyncio
from typing import Any

from langchain.agents import create_agent

from .config import DEFAULT_AGENT_CONFIG
from .prompts import get_prompt
from .tools import get_mcp_tools


async def create_agent_with_mcp_tools(
    prompt_name: str = "email_assistant", selected_tools: list = None, agent_config=None
):
    """
    Create an agent with MCP tools using modular configuration.

    Args:
        prompt_name: Name of the prompt to use from prompts.py
        selected_tools: List of specific tool names to use, or None for default
        agent_config: Agent configuration, uses default if None
    """
    if agent_config is None:
        agent_config = DEFAULT_AGENT_CONFIG

    # Get the system prompt
    system_prompt = get_prompt(prompt_name)

    # Get filtered MCP tools
    tools = await get_mcp_tools(selected_tools)

    if not tools:
        print("Warning: No tools available!")
    else:
        tool_names = [tool.name for tool in tools]
        print(f"Agent created with tools: {tool_names}")

    return create_agent(
        agent_config.model,
        tools=tools,
        system_prompt=system_prompt,
    )


# Default configuration - using retrieve_documents tool with email assistant prompt
DEFAULT_SELECTED_TOOLS = ["retrieve_documents"]

# Create the agent synchronously by running the async function
agent = asyncio.run(
    create_agent_with_mcp_tools(
        prompt_name="email_assistant", selected_tools=DEFAULT_SELECTED_TOOLS
    )
)
