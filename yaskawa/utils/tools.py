import os

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from openai import OpenAI

load_dotenv()


@tool
def send_email(to: str, subject: str, body: str):
    """Send an email"""
    email = {"to": to, "subject": subject, "body": body}
    # ... email sending logic

    return f"Email sent to {to}"


@tool
def web_search(query: str) -> str:
    """Perform a web search using OpenAI models"""
    model = {"name": "gpt-5", "reasoning_effort": "medium"}
    domains = ["knowledge.motoman.com"]

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.responses.create(
        model=model["name"],
        tools=[
            {
                "type": "web_search",
                "filters": {"allowed_domains": domains},
            }
        ],
        reasoning={"effort": model["reasoning_effort"]},
        input=query,
        tool_choice="auto",
        include=["web_search_call.action.sources"],
    )

    return f"OpenAI Response: '{response.output_text}'"


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
