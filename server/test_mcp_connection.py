#!/usr/bin/env python3
"""Test MCP connection to the weather server."""

import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_mcp_connection():
    """Test connection to the MCP server."""
    print("Testing MCP connection to weather server...")
    
    try:
        # Connect to the MCP server
        streams_context = streamablehttp_client(
            url="http://localhost:8124/mcp",
            headers={},
        )
        
        read_stream, write_stream, _ = await streams_context.__aenter__()
        
        session_context = ClientSession(read_stream, write_stream)
        session: ClientSession = await session_context.__aenter__()
        
        print("✅ Connected to MCP server")
        
        # Initialize the session
        await session.initialize()
        print("✅ Session initialized")
        
        # List tools
        tools_result = await session.list_tools()
        tools = tools_result.tools
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test a simple tool call
        if tools:
            tool = tools[0]
            print(f"\nTesting tool: {tool.name}")
            
            # Call the tool with sample parameters
            if tool.name == "get_alerts":
                result = await session.call_tool(tool.name, {"state": "CA"})
            elif tool.name == "get_forecast":
                result = await session.call_tool(tool.name, {"latitude": 40.7128, "longitude": -74.006})
            else:
                print(f"Unknown tool: {tool.name}")
                return
            
            print(f"✅ Tool call successful: {result.content}")
        
        # Clean up
        await session_context.__aexit__(None, None, None)
        await streams_context.__aexit__(None, None, None)
        
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
