import asyncio

from fastmcp import Client

client = Client("http://localhost:8000/sse")


async def call_tool():
    async with client:
        result = await client.call_tool(
            "search_with_regex",
            {
                "context_path": "examples/workspace/longbench0_context.txt",
                "regex_pattern": " kademor ",
            },
        )
        print(result)


asyncio.run(call_tool())
