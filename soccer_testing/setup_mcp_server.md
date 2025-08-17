# Quick MCP Server Setup

## Step 1: Install Node.js MCP Server
Open terminal in the soccer_testing folder and run:

```bash
cd C:\Users\fstr2\Desktop\sports\soccer_testing
npm install @yeonupark/mcp-soccer-data@latest
```

## Step 2: Set Environment Variable
```bash
# Windows Command Prompt:
set SOCCERDATA_API_KEY=a9f37754a540df435e8c40ed89c08565166524ed

# Windows PowerShell:
$env:SOCCERDATA_API_KEY="a9f37754a540df435e8c40ed89c08565166524ed"

# Or create .env file:
echo SOCCERDATA_API_KEY=a9f37754a540df435e8c40ed89c08565166524ed > .env
```

## Step 3: Run MCP Server
```bash
npx @yeonupark/mcp-soccer-data@latest
```

Server should start and show something like:
```
MCP Server running on http://localhost:3000/mcp
```

## Step 4: Test Our Script
In another terminal:
```bash
python test_single_team_mcp.py
```

## If MCP Server Doesn't Work
We can fall back to direct API testing with:
```bash
python test_soccerdataapi.py --endpoint leagues
```