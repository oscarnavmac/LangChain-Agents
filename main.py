from yaskawa.agent import agent


async def main():
    # Example usage of the agent
    user_input = "Hello."
    response = await agent.ainvoke(
        {"input": {"messages": [{"role": "user", "content": user_input}]}}
    )
    return response


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(main())
    print(result)
