import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_agent_with_mcp_tools():
    client = MultiServerMCPClient(
        {
            "rag": {
                "transport": "sse",
                "url": "https://rshp-mcp.fly.dev/mcp",
            }
        }
    )
    tools = await client.get_tools()

    return create_agent(
        "openai:gpt-4o",
        tools=tools,
        system_prompt="You are an email assistant. Always use the send_email tool.",
    )


# Create the agent synchronously by running the async function
agent = asyncio.run(create_agent_with_mcp_tools())
