import asyncio

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.utils.middleware import (
    SafetyInputGuardrailMiddleware,
    SafetyOutputGuardrailMiddleware,
)
from src.utils.tools import get_reshape_mcp_tools

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
    mcp_tools = await get_reshape_mcp_tools("retrieve_documents")

    return create_agent(
        model,
        tools=mcp_tools + [send_email],
        middleware=[
            SafetyInputGuardrailMiddleware(),
            SafetyOutputGuardrailMiddleware(),
        ],
        system_prompt=read_prompt_from_md("src/Yaskawa_prompt_final.md"),
    )


# Create the agent synchronously by running the async function
agent = asyncio.run(create_agent_with_mcp_tools())
