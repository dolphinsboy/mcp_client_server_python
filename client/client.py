"""MCP Streamable HTTP Client"""

import argparse
import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

import httpx
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    """MCP Client for interacting with an MCP Streamable HTTP server"""

    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Get OpenAI configuration from environment variables
        self.openai_key = os.getenv("OPENAI_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL")
        
        if not self.openai_key:
            raise ValueError("OPENAI_KEY environment variable is required")
        if not self.openai_base_url:
            raise ValueError("OPENAI_BASE_URL environment variable is required")
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
        )

    async def connect_to_streamable_http_server(
        self, server_url: str, headers: Optional[dict] = None
    ):
        """Connect to an MCP server running with HTTP Streamable transport"""
        self._streams_context = streamablehttp_client(  # pylint: disable=W0201
            url=server_url,
            headers=headers or {},
        )
        read_stream, write_stream, _ = await self._streams_context.__aenter__()  # pylint: disable=E1101

        self._session_context = ClientSession(read_stream, write_stream)  # pylint: disable=W0201
        self.session: ClientSession = await self._session_context.__aenter__()  # pylint: disable=C2801

        await self.session.initialize()

    async def call_openai_api(self, messages, tools=None):
        """Make a call to OpenAI-compatible API"""
        payload = {
            "model": "gpt-4",
            "messages": messages,
            "max_tokens": 1000,
        }
        
        if tools:
            payload["tools"] = tools
        
        response = await self.http_client.post(
            f"{self.openai_base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def extract_text_content(self, content):
        """Extract text from MCP content objects"""
        if hasattr(content, 'text'):
            return content.text
        elif isinstance(content, str):
            return content
        elif isinstance(content, dict) and 'text' in content:
            return content['text']
        else:
            return str(content)

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                }
            }
            for tool in response.tools
        ]
        print(available_tools)

        # Initial OpenAI API call
        response_data = await self.call_openai_api(messages, available_tools)
        print(response_data)

        # Process response and handle tool calls
        final_text = []

        for choice in response_data.get("choices", []):
            message = choice.get("message", {})
            
            if message.get("content"):
                final_text.append(message["content"])
            
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args_str = tool_call["function"]["arguments"]

                    # Parse JSON arguments
                    try:
                        tool_args = json.loads(tool_args_str)
                    except json.JSONDecodeError as e:
                        final_text.append(f"Error parsing tool arguments: {e}")
                        continue

                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    
                    # Extract text content from result
                    result_text = self.extract_text_content(result.content)
                    
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                    # Continue conversation with tool results
                    messages.append({"role": "assistant", "content": message.get("content", "")})
                    messages.append({"role": "user", "content": result_text})

                    # Get next response from OpenAI
                    response_data = await self.call_openai_api(messages)

                    if response_data.get("choices") and response_data["choices"][0].get("message", {}).get("content"):
                        final_text.append(response_data["choices"][0]["message"]["content"])

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:  # pylint: disable=W0125
            await self._streams_context.__aexit__(None, None, None)  # pylint: disable=E1101
        await self.http_client.aclose()


async def main():
    """Main function to run the MCP client"""
    parser = argparse.ArgumentParser(description="Run MCP Streamable http based Client")
    parser.add_argument(
        "--mcp-localhost-port", type=int, default=8123, help="Localhost port to bind to"
    )
    args = parser.parse_args()

    client = MCPClient()

    try:
        await client.connect_to_streamable_http_server(
            f"http://localhost:{args.mcp_localhost_port}/mcp"
        )
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
