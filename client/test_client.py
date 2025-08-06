#!/usr/bin/env python3
"""Simple test script for the MCP client"""

import asyncio
import os
from client import MCPClient

async def test_client():
    """Test the MCP client with a simple query"""
    # Set up test environment variables
    os.environ["OPENAI_KEY"] = "test-key"
    os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"
    
    client = MCPClient()
    
    try:
        # Connect to the server
        await client.connect_to_streamable_http_server("http://localhost:8123/mcp")
        print("✅ Connected to MCP server successfully")
        
        # List available tools
        tools_response = await client.session.list_tools()
        print(f"✅ Found {len(tools_response.tools)} tools:")
        for tool in tools_response.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        print("\n✅ Client test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(test_client()) 