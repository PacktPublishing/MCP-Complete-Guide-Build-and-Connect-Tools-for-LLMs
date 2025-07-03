from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import traceback

server_params = StdioServerParameters(
    command="uv",
    args=["--directory", "C:\\MCP\\code\\mcp-client", "run", "server.py"],  # Optional command line arguments
)

async def run():
    try:
        print("Starting stdio_client...")
        async with stdio_client(server_params) as (read, write):
            print("Client connected, creating session...")
            async with ClientSession(read, write) as session:

                print("Initializing session...")
                await session.initialize()

                # TOOLS

                print("Listing tools...")
                tools = await session.list_tools()
                print("Available tools:", tools)

                print("Calling tool...")
                result = await session.call_tool("get_weather", arguments={"location": "San Francisco"})
                print("Tool result:", result)

                # RESOURCES

                print("Listing resources...")
                resources = await session.list_resources()
                print("Available resources:", resources)

                print("Listing resources templates...")
                resources = await session.list_resource_templates()
                print("Available resource templates:", resources)

                print("Getting resource")
                resource = await session.read_resource("weather://statement")
                print(resource)

                print("Getting resource template")
                resource = await session.read_resource("weather://Vancouver/statement")
                print(resource)

                # PROMPTS

                print("Listing prompts...")
                prompts = await session.list_prompts()
                print("Available prompts templates:", prompts)

                print("Prompt tool...")
                result = await session.get_prompt("get_prompt", arguments={"topic": "Water Cycle"})
                print("Prompt result:", result)



    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
