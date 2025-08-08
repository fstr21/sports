#!/usr/bin/env python3
"""
Odds CLI client for sports betting odds data.

This client provides access to sports betting odds using the Wagyu Odds MCP server.
It is completely separate from ESPN data and uses only the Wagyu Odds API.
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional, List
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class OddsMCPClient:
    """
    MCP client specifically for the Wagyu Odds server.
    """
    
    def __init__(self):
        self.server_script_path = self._get_odds_server_path()
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        
    def _get_odds_server_path(self) -> str:
        """Get the path to the Wagyu Odds MCP server script."""
        current_dir = Path(__file__).parent
        server_path = current_dir.parent / "sports_mcp" / "wagyu_sports" / "mcp_server" / "odds_client_server.py"
        
        if not server_path.exists():
            raise Exception(f"Wagyu Odds MCP server script not found at {server_path}")
        
        return str(server_path)
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        """Start the Wagyu Odds MCP server process."""
        try:
            # Start the MCP server as a subprocess
            self.process = subprocess.Popen(
                [sys.executable, self.server_script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Initialize the MCP session
            await self._initialize_session()
            
        except Exception as e:
            raise Exception(f"Failed to start Wagyu Odds MCP server: {e}")
    
    async def disconnect(self):
        """Stop the MCP server process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
    
    async def _initialize_session(self):
        """Initialize the MCP session with the server."""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "odds-cli",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        if "error" in response:
            raise Exception(f"MCP initialization failed: {response['error']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        await self._send_notification(initialized_notification)
    
    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request and wait for response."""
        if not self.process:
            raise Exception("Wagyu Odds MCP server not connected")
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if not response_line:
                raise Exception("Wagyu Odds MCP server closed connection")
            
            response = json.loads(response_line.strip())
            return response
            
        except Exception as e:
            raise Exception(f"Failed to communicate with Wagyu Odds MCP server: {e}")
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process:
            raise Exception("Wagyu Odds MCP server not connected")
        
        try:
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
        except Exception as e:
            raise Exception(f"Failed to send notification: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Wagyu Odds MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error = response["error"]
            raise Exception(f"Tool call failed: {error.get('message', 'Unknown error')}")
        
        return response.get("result", {})

def format_sports_list(data: str) -> str:
    """Format sports list for display."""
    try:
        sports_data = json.loads(data)
        
        if isinstance(sports_data, dict) and "error" in sports_data:
            return f"❌ Error: {sports_data['error']}"
        
        if not isinstance(sports_data, list):
            return "❌ Unexpected data format"
        
        output = ["📊 Available Sports:"]
        output.append("-" * 50)
        
        for sport in sports_data:
            if isinstance(sport, dict):
                key = sport.get('key', 'unknown')
                title = sport.get('title', 'Unknown Sport')
                active = sport.get('active', False)
                status = "🟢 Active" if active else "🔴 Inactive"
                output.append(f"{key:<25} | {title:<30} | {status}")
            else:
                output.append(str(sport))
        
        return "\n".join(output)
        
    except json.JSONDecodeError:
        return f"❌ Invalid JSON response: {data}"

def format_odds_data(data: str, sport: str) -> str:
    """Format odds data for display."""
    try:
        odds_data = json.loads(data)
        
        if isinstance(odds_data, dict) and "error" in odds_data:
            return f"❌ Error: {odds_data['error']}"
        
        if not isinstance(odds_data, list):
            return "❌ Unexpected data format"
        
        if not odds_data:
            return f"📊 No odds available for {sport}"
        
        output = [f"📊 Odds for {sport.upper()}:"]
        output.append("-" * 80)
        
        for game in odds_data[:10]:  # Limit to first 10 games
            if isinstance(game, dict):
                home_team = game.get('home_team', 'Unknown')
                away_team = game.get('away_team', 'Unknown')
                commence_time = game.get('commence_time', 'Unknown')
                
                output.append(f"\n🏈 {away_team} @ {home_team}")
                output.append(f"   Time: {commence_time}")
                
                bookmakers = game.get('bookmakers', [])
                if bookmakers:
                    for book in bookmakers[:3]:  # Show first 3 bookmakers
                        book_name = book.get('title', 'Unknown Book')
                        markets = book.get('markets', [])
                        
                        output.append(f"   📖 {book_name}:")
                        
                        for market in markets:
                            market_key = market.get('key', 'unknown')
                            outcomes = market.get('outcomes', [])
                            
                            if market_key == 'h2h' and outcomes:
                                for outcome in outcomes:
                                    name = outcome.get('name', 'Unknown')
                                    price = outcome.get('price', 'N/A')
                                    output.append(f"      {name}: {price}")
                else:
                    output.append("   No bookmaker data available")
            else:
                output.append(str(game))
        
        if len(odds_data) > 10:
            output.append(f"\n... and {len(odds_data) - 10} more games")
        
        return "\n".join(output)
        
    except json.JSONDecodeError:
        return f"❌ Invalid JSON response: {data}"

def format_quota_info(data: str) -> str:
    """Format quota information for display."""
    try:
        quota_data = json.loads(data)
        
        if isinstance(quota_data, dict) and "error" in quota_data:
            return f"❌ Error: {quota_data['error']}"
        
        output = ["📊 API Quota Information:"]
        output.append("-" * 30)
        
        if isinstance(quota_data, dict):
            remaining = quota_data.get('remaining_requests', 'Unknown')
            used = quota_data.get('used_requests', 'Unknown')
            
            output.append(f"Remaining requests: {remaining}")
            output.append(f"Used requests: {used}")
        else:
            output.append(str(quota_data))
        
        return "\n".join(output)
        
    except json.JSONDecodeError:
        return f"❌ Invalid JSON response: {data}"

async def get_sports(all_sports: bool = False, output_json: bool = False) -> None:
    """Get available sports."""
    try:
        logger.info("Fetching available sports from Wagyu Odds API")
        
        async with OddsMCPClient() as client:
            response = await client.call_tool("get_sports", {"all_sports": all_sports})
            
            # Extract content from MCP response
            content = response.get("content", [])
            if content and isinstance(content, list):
                data = content[0].get("text", "{}")
            else:
                data = "{}"
        
        if output_json:
            print(data)
        else:
            print(format_sports_list(data))
            
    except Exception as e:
        logger.error(f"Error fetching sports: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

async def get_odds(sport: str, regions: Optional[str] = None, markets: Optional[str] = None,
                  odds_format: Optional[str] = None, date_format: Optional[str] = None,
                  output_json: bool = False) -> None:
    """Get odds for a specific sport."""
    try:
        logger.info(f"Fetching odds for {sport}")
        
        arguments = {"sport": sport}
        if regions:
            arguments["regions"] = regions
        if markets:
            arguments["markets"] = markets
        if odds_format:
            arguments["odds_format"] = odds_format
        if date_format:
            arguments["date_format"] = date_format
        
        async with OddsMCPClient() as client:
            response = await client.call_tool("get_odds", arguments)
            
            # Extract content from MCP response
            content = response.get("content", [])
            if content and isinstance(content, list):
                data = content[0].get("text", "{}")
            else:
                data = "{}"
        
        if output_json:
            print(data)
        else:
            print(format_odds_data(data, sport))
            
    except Exception as e:
        logger.error(f"Error fetching odds for {sport}: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

async def get_quota() -> None:
    """Get API quota information."""
    try:
        logger.info("Fetching API quota information")
        
        async with OddsMCPClient() as client:
            response = await client.call_tool("get_quota_info", {})
            
            # Extract content from MCP response
            content = response.get("content", [])
            if content and isinstance(content, list):
                data = content[0].get("text", "{}")
            else:
                data = "{}"
        
        print(format_quota_info(data))
            
    except Exception as e:
        logger.error(f"Error fetching quota info: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Odds CLI - Sports Betting Odds Data (Wagyu Odds API)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sports --all
  %(prog)s odds basketball_nba --regions us --markets h2h,spreads
  %(prog)s odds americanfootball_nfl --json
  %(prog)s quota

Common sport keys:
  basketball_nba, americanfootball_nfl, baseball_mlb, icehockey_nhl,
  soccer_epl, soccer_uefa_champs_league, tennis_atp_french_open

Note: This client uses the Wagyu Odds API, completely separate from ESPN data.
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sports command
    sports_parser = subparsers.add_parser('sports', help='List available sports')
    sports_parser.add_argument('--all', action='store_true', help='Include out-of-season sports')
    sports_parser.add_argument('--json', action='store_true', help='Output raw JSON')
    
    # Odds command
    odds_parser = subparsers.add_parser('odds', help='Get odds for a sport')
    odds_parser.add_argument('sport', help='Sport key (e.g., basketball_nba)')
    odds_parser.add_argument('--regions', help='Comma-separated regions (e.g., us,uk)')
    odds_parser.add_argument('--markets', help='Comma-separated markets (e.g., h2h,spreads)')
    odds_parser.add_argument('--odds-format', choices=['decimal', 'american'], help='Odds format')
    odds_parser.add_argument('--date-format', choices=['unix', 'iso'], help='Date format')
    odds_parser.add_argument('--json', action='store_true', help='Output raw JSON')
    
    # Quota command
    quota_parser = subparsers.add_parser('quota', help='Get API quota information')
    
    return parser

async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'sports':
            await get_sports(args.all, args.json)
        elif args.command == 'odds':
            await get_odds(args.sport, args.regions, args.markets, 
                          args.odds_format, args.date_format, args.json)
        elif args.command == 'quota':
            await get_quota()
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())