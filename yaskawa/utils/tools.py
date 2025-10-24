import os

from composio import Composio
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from openai import OpenAI

load_dotenv()


def gmail_send_email(
    recipient_email: str, body: str, subject: str, is_html: bool = False
) -> None:
    """Send an email from Gmail using Composio"""
    composio = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    externalUserId = os.environ.get("COMPOSIO_USER_ID")
    connected_account_id = os.environ.get("COMPOSIO_ACCOUNT_ID")

    return composio.tools.execute(
        slug="GMAIL_SEND_EMAIL",
        arguments={
            "recipient_email": recipient_email,
            "body": body,
            "subject": subject,
            "is_html": is_html,
        },
        user_id=externalUserId,
        version="20251023_00",
        connected_account_id=connected_account_id,
    )


@tool
def web_search(query: str) -> str:
    """Perform a web search using OpenAI models"""
    model = {"name": "gpt-5", "reasoning_effort": "medium"}
    domains = ["knowledge.motoman.com", "www.motoman.com"]

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
