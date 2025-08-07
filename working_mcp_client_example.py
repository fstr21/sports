#!/usr/bin/env python3
"""
Working example of how to use your MCP proxy
Focus on the servers that are actually working: sports-ai and fetch
"""
import asyncio
from mcp.client.sse import sse_client
from mcp import ClientSession
import json

class WorkingMCPClient:
    def __init__(self):
        self.proxy_url = "http://localhost:9091"
        self.headers = {"Authorization": "Bearer sports-betting-token"}
    
    async def connect_and_explore_server(self, server_name):
        """Connect to a working server and explore its capabilities"""
        
        print(f"\nCONNECTING TO {server_name.upper()}")
        print("=" * 40)
        
        sse_url = f"{self.proxy_url}/{server_name}/sse"
        
        try:
            async with sse_client(sse_url, headers=self.headers) as streams:
                read, write = streams
                async with ClientSession(read, write) as session:
                    
                    # Initialize the session
                    print("Initializing session...")
                    init_result = await session.initialize()
                    print(f"✓ Connected to {server_name}")
                    
                    # Get server capabilities
                    print(f"Server capabilities: {init_result.capabilities}")
                    
                    # List available tools
                    print("\nListing tools...")
                    tools_result = await session.list_tools()
                    print(f"Available tools ({len(tools_result.tools)}):")
                    for tool in tools_result.tools:
                        print(f"  - {tool.name}: {tool.description}")
                    
                    # List available resources
                    print("\nListing resources...")
                    try:
                        resources_result = await session.list_resources()
                        print(f"Available resources ({len(resources_result.resources)}):")
                        for resource in resources_result.resources:
                            print(f"  - {resource.name} ({resource.uri})")
                    except Exception as e:
                        print(f"No resources available: {e}")
                    
                    # Try calling the first tool (if any)
                    if tools_result.tools:
                        first_tool = tools_result.tools[0]
                        print(f"\nTesting tool: {first_tool.name}")
                        try:
                            # Call with empty arguments first
                            result = await session.call_tool(first_tool.name, {})
                            print(f"✓ Tool result: {result}")
                        except Exception as e:
                            print(f"Tool call failed: {e}")
                            
                            # Try with some common arguments if the tool expects them
                            if "url" in str(first_tool.parameters):
                                try:
                                    result = await session.call_tool(first_tool.name, {
                                        "url": "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
                                    })
                                    print(f"✓ Tool result with URL: {result}")
                                except Exception as e2:
                                    print(f"Tool call with URL also failed: {e2}")
                    
                    return True
                    
        except Exception as e:
            print(f"✗ Failed to connect to {server_name}: {e}")
            return False

    async def test_fetch_server_specifically(self):
        """Test the fetch server with a real ESPN API call"""
        
        print("\nTESTING FETCH SERVER WITH ESPN API")
        print("=" * 40)
        
        sse_url = f"{self.proxy_url}/fetch/sse"
        
        try:
            async with sse_client(sse_url, headers=self.headers) as streams:
                read, write = streams
                async with ClientSession(read, write) as session:
                    
                    await session.initialize()
                    
                    # Get the fetch tool
                    tools = await session.list_tools()
                    fetch_tool = next((t for t in tools.tools if "fetch" in t.name.lower()), None)
                    
                    if fetch_tool:
                        print(f"Using tool: {fetch_tool.name}")
                        
                        # Test with ESPN NBA scoreboard
                        espn_url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
                        result = await session.call_tool(fetch_tool.name, {"url": espn_url})
                        
                        print("✓ ESPN API call successful!")
                        
                        # Parse the result to show some actual data
                        if hasattr(result, 'content') and result.content:
                            try:
                                data = json.loads(result.content[0].text)
                                if 'events' in data:
                                    print(f"Found {len(data['events'])} NBA games")
                                    for event in data['events'][:2]:  # Show first 2 games
                                        home_team = event.get('competitions', [{}])[0].get('competitors', [{}])[0].get('team', {}).get('displayName', 'Unknown')
                                        away_team = event.get('competitions', [{}])[0].get('competitors', [{}])[1].get('team', {}).get('displayName', 'Unknown')
                                        print(f"  Game: {away_team} @ {home_team}")
                            except:
                                print("Got data but couldn't parse game details")
                        
                        return True
                    else:
                        print("No fetch tool found")
                        return False
                        
        except Exception as e:
            print(f"✗ Fetch server test failed: {e}")
            return False

async def main():
    client = WorkingMCPClient()
    
    print("MCP PROXY WORKING CLIENT EXAMPLE")
    print("=" * 50)
    
    # Test the working servers
    working_servers = ["sports-ai", "fetch"]
    
    results = {}
    for server in working_servers:
        success = await client.connect_and_explore_server(server)
        results[server] = success
    
    # Specific test for fetch server
    if results.get("fetch"):
        await client.test_fetch_server_specifically()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for server, success in results.items():
        status = "✓ WORKING" if success else "✗ FAILED"
        print(f"{server}: {status}")
    
    print("\nHow to use your proxy:")
    print("1. sports-ai server: Custom sports analysis tools")
    print("2. fetch server: HTTP requests to ESPN, etc.")
    print("3. Connect via: http://localhost:9091/{server}/sse")
    print("4. Auth: Authorization: Bearer sports-betting-token")

if __name__ == "__main__":
    asyncio.run(main())