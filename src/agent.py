import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model_name="gpt-4.1")


# read prompt from md file
def read_prompt_from_md(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def send_email(to: str, subject: str, body: str):
    """Send an email"""
    email = {"to": to, "subject": subject, "body": body}
    # ... email sending logic

    return f"Email sent to {to}"


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
        model,
        tools=tools + [send_email],
        system_prompt=read_prompt_from_md("src/Yaskawa_prompt_final.md"),
    )


# Create the agent synchronously by running the async function
agent = asyncio.run(create_agent_with_mcp_tools())
