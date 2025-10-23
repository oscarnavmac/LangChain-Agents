import asyncio

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from yaskawa.utils.middleware import (
    SafetyInputGuardrailMiddleware,
    SafetyOutputGuardrailMiddleware,
)
from yaskawa.utils.tools import get_reshape_mcp_tools, gmail_send_email, web_search

model = ChatOpenAI(model_name="gpt-4.1")


# read prompt from md file
def read_prompt_from_md(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


async def create_agent_with_mcp_tools():
    mcp_tools = await get_reshape_mcp_tools(["retrieve_documents"])

    return create_agent(
        model,
        tools=mcp_tools + [gmail_send_email, web_search],
        middleware=[
            SafetyInputGuardrailMiddleware(),
            SafetyOutputGuardrailMiddleware(),
        ],
        system_prompt=read_prompt_from_md("yaskawa/Yaskawa_prompt.md"),
    )


# Create the agent synchronously by running the async function
agent = asyncio.run(create_agent_with_mcp_tools())
