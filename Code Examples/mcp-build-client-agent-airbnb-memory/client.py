from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import traceback
import json

import os
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found"

# Define parameters for two servers
server_params_1 = StdioServerParameters(
    command="npx",
    args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
)
server_params_2 = StdioServerParameters(
    command="uv",
    args=["--directory", "C:\\MCP\\code\\mcp-build-memory", "run", "server.py"],  # Change to your second server
)

async def run():
    try:
        print("Starting stdio_clients for both servers...")
        async with stdio_client(server_params_1) as (read1, write1), stdio_client(server_params_2) as (read2, write2):
            print("Clients connected, creating sessions...")
            async with ClientSession(read1, write1) as session1, ClientSession(read2, write2) as session2:

                # Initialize both servers
                print("Initializing sessions...")
                await session1.initialize()
                await session2.initialize()

                # Get tools from both servers
                print("Listing tools from both servers...")
                tools_result_1 = await session1.list_tools()
                tools_result_2 = await session2.list_tools()

                # Combine tools (simple merge, you can deduplicate by name if needed)
                combined_tools = tools_result_1.tools + tools_result_2.tools
                print("Available tools (combined):", combined_tools)

                openai_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    for tool in combined_tools
                ]

                client = OpenAI()
                messages = []
                while True:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ("exit", "quit"):  # Allow user to exit
                        print("Exiting chat.")
                        break
                    if not user_input:
                        continue
                    messages.append({"role": "user", "content": user_input})

                    response = client.chat.completions.create(
                        model='gpt-4o',
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto",
                    )

                    messages.append(response.choices[0].message)
                    tool_calls = response.choices[0].message.tool_calls

                    # Handle any tool calls
                    if response.choices[0].message.tool_calls:
                        for tool_execution in tool_calls:
                            # Decide which session to use based on tool name
                            if any(t.name == tool_execution.function.name for t in tools_result_1.tools):
                                session = session1
                            else:
                                session = session2
                            # Execute tool call
                            result = await session.call_tool(
                                tool_execution.function.name,
                                arguments=json.loads(tool_execution.function.arguments),
                            )

                            # Add tool response to conversation
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_execution.id,
                                    "content": result.content[0].text,
                                }
                            )

                            # Get response from LLM
                            response = client.chat.completions.create(
                                model='gpt-4o',
                                messages=messages,
                                tools=openai_tools,
                                tool_choice="auto",
                            )

                            if response.choices[0].finish_reason == "tool_calls":
                                tool_calls.extend(response.choices[0].message.tool_calls)

                            if response.choices[0].finish_reason == "stop":
                                print(f"AI: {response.choices[0].message.content}")
                                messages.append(response.choices[0].message)
                                break
                    else:
                        print(f"AI: {response.choices[0].message.content}")
                        messages.append(response.choices[0].message)

    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())