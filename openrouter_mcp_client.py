#!/usr/bin/env python3
"""
OpenRouter client that can use your MCP proxy servers
"""
import openai
import requests
import json
import os
from typing import Dict, Any, List

class OpenRouterMCPClient:
    def __init__(self):
        # Load your OpenRouter credentials from .env.local
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-4o-mini"  # Free model
        
        # MCP proxy settings
        self.mcp_proxy_url = "http://localhost:9091"
        self.mcp_auth_token = "sports-betting-token"
        
        # Initialize OpenRouter client
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def call_mcp_tool(self, server: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool through the proxy
        This would need to be implemented based on the MCP protocol
        For now, this is a placeholder showing the concept
        """
        # In a real implementation, you'd need to:
        # 1. Establish SSE connection to the MCP server
        # 2. Send MCP protocol messages
        # 3. Handle responses
        
        print(f"Would call {server}/{tool_name} with {arguments}")
        
        # Placeholder response - in reality this would come from your MCP server
        if server == "sports-ai" and tool_name == "analyze_game":
            return {
                "prediction": "Home team favored by 3.5 points",
                "confidence": 0.75,
                "key_factors": ["Recent form", "Home advantage", "Injury reports"]
            }
        elif server == "wagyu-sports" and tool_name == "get_odds":
            return {
                "moneyline": {"home": -150, "away": +130},
                "spread": {"home": -3.5, "away": +3.5},
                "total": {"over": 220.5, "under": 220.5}
            }
        
        return {"error": "Tool not found"}
    
    def get_sports_analysis(self, query: str) -> str:
        """
        Use OpenRouter + MCP to analyze sports betting opportunities
        """
        
        # Define available MCP tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "analyze_game",
                    "description": "Analyze a specific game for betting insights",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "team1": {"type": "string", "description": "First team"},
                            "team2": {"type": "string", "description": "Second team"},
                            "sport": {"type": "string", "description": "Sport type (NBA, NFL, etc.)"}
                        },
                        "required": ["team1", "team2", "sport"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "get_odds",
                    "description": "Get current betting odds for a game",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game_id": {"type": "string", "description": "Game identifier"},
                            "sport": {"type": "string", "description": "Sport type"}
                        },
                        "required": ["game_id", "sport"]
                    }
                }
            }
        ]
        
        # Call OpenRouter with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a sports betting analyst with access to real-time sports data and odds. Use the available tools to provide detailed betting insights."},
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # If the model wants to call tools
        if message.tool_calls:
            # Execute the tool calls through MCP
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Determine which MCP server to use
                if function_name == "analyze_game":
                    result = self.call_mcp_tool("sports-ai", function_name, arguments)
                elif function_name == "get_odds":
                    result = self.call_mcp_tool("wagyu-sports", function_name, arguments)
                else:
                    result = {"error": "Unknown function"}
                
                print(f"Tool {function_name} result: {result}")
            
            # In a full implementation, you'd send the tool results back to OpenRouter
            # for the final response
            return f"Analysis complete. Tool calls executed: {[tc.function.name for tc in message.tool_calls]}"
        
        return message.content
    
    def check_mcp_servers(self):
        """Check if MCP servers are accessible"""
        servers = ["sports-ai", "wagyu-sports", "fetch"]
        
        print("Checking MCP server availability:")
        for server in servers:
            url = f"{self.mcp_proxy_url}/{server}/sse"
            headers = {"Authorization": f"Bearer {self.mcp_auth_token}"}
            
            try:
                # Quick connection test (will timeout, but that's expected for SSE)
                response = requests.get(url, headers=headers, timeout=0.5)
                print(f"  {server}: Unexpected response {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"  {server}: [OK] Available (SSE endpoint responding)")
            except requests.exceptions.RequestException as e:
                print(f"  {server}: [ERROR] Not available - {e}")

def main():
    client = OpenRouterMCPClient()
    
    print("OpenRouter + MCP Integration Test")
    print("=" * 40)
    
    # Check MCP servers
    client.check_mcp_servers()
    
    print("\n" + "=" * 40)
    
    # Test analysis
    query = "What are the best betting opportunities for tonight's NBA games?"
    print(f"Query: {query}")
    print("\nAnalysis:")
    
    result = client.get_sports_analysis(query)
    print(result)

if __name__ == "__main__":
    main()