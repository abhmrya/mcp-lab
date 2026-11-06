import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--active",
            "python",
            "servers/first_server.py",
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            print("Connected to MCP Server")

            tools = await session.list_tools()

            print("\nAvailable Tools:")

            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")


            resources = await session.list_resources()

            print("\nAvailable Resources:")

            for resource in resources.resources:
                print(f"- {resource.name}: {resource.uri}")

            resource_result = await session.read_resource(
                "app://info"
            )

            print("\nResource Result:")
            print(resource_result.contents)


            prompts = await session.list_prompts()

            print("\nAvailable Prompts:")

            for prompt in prompts.prompts:
                print(f"- {prompt.name}: {prompt.description}")

            prompt_result = await session.get_prompt(
                "product_analysis",
                arguments={
                    "product_name": "Gaming Laptop",
                    "price": "75000",
                },
            )

            print("\nPrompt Result:")
            print(prompt_result.messages)


            result = await session.call_tool(
                "add",
                arguments={
                    "a": 10,
                    "b": 20,
                },
            )

            print("\nTool Result:")
            print(result.content)


if __name__ == "__main__":
    asyncio.run(main())