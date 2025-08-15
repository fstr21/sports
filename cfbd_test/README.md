# CFBD MCP Server Testing

This folder contains a self-contained testing environment for the College Football Data (CFBD) MCP server from:
https://github.com/MCP-Mirror/lenwood_cfbd-mcp-server

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your CFBD API key in `.env`:
```
CFBD_API_KEY=your_api_key_here
```

3. Configure MCP server in `mcp_config.json`

4. Run tests:
```bash
python test_cfbd_endpoints.py
```

## Available Endpoints

The CFBD MCP server provides access to college football data including:
- Team information
- Game data
- Player statistics
- Recruiting data
- Betting lines
- And more...

## Files

- `test_cfbd_endpoints.py` - Main test script
- `mcp_config.json` - MCP server configuration
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create this file)