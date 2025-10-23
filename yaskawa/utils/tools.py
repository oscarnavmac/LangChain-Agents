from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_reshape_mcp_tools(tool_names: list[str]):
    client = MultiServerMCPClient(
        {
            "rag": {
                "transport": "sse",
                "url": "https://rshp-mcp.fly.dev/mcp",
            }
        }
    )
    tools = await client.get_tools()
    if tool_names:
        tools = [tool for tool in tools if tool.name in tool_names]

    return tools
