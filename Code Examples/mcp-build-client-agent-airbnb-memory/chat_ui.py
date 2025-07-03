import streamlit as st
import asyncio
import json
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
import os
from dotenv import load_dotenv
import sys

# Set the event loop policy to WindowsProactorEventLoopPolicy at the top of the file to fix subprocess support on Windows.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Load environment variables
load_dotenv()
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY not found"

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
)

def get_openai_tools(tools_result):
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools_result.tools
    ]

async def chat_response(messages, session, openai_tools, client):
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
                messages.append(response.choices[0].message)
                return response.choices[0].message.content
    else:
        messages.append(response.choices[0].message)
        return response.choices[0].message.content

def sync_chat_response(messages, user_input):
    async def _chat():
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                openai_tools = get_openai_tools(tools_result)
                client = OpenAI()
                messages.append({"role": "user", "content": user_input})
                response = await chat_response(messages, session, openai_tools, client)
                return response
    return asyncio.run(_chat())

def main():
    st.title("Airbnb Chatbot (MCP + OpenAI)")
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "history" not in st.session_state:
        st.session_state["history"] = []
    reset = st.button("Reset Chat")
    if reset:
        st.session_state["messages"] = []
        st.session_state["history"] = []
        st.rerun()
    user_input = st.text_input("You:", key="user_input")
    if st.button("Send") and user_input:
        with st.spinner("Thinking..."):
            try:
                response = sync_chat_response(st.session_state["messages"], user_input)
                st.session_state["history"].append((user_input, response))
                st.rerun()
            except Exception as e:
                st.error("An error occurred:")
                st.error(traceback.format_exc())
    for user, bot in st.session_state["history"]:
        st.markdown(f"**You:** {user}")
        st.markdown(f"**AI:** {bot}")

def run_streamlit():
    main()

if __name__ == "__main__":
    run_streamlit()
