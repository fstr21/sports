# Enhanced Soccer Betting Analyzer - Remote Testing

This folder contains tests and demos for your deployed MCP server.

## 📁 Files:

### **test_remote_mcp.py** - Automated Test Suite
- **Purpose**: Verify all 5 MCP tools work correctly
- **Usage**: `python test_remote_mcp.py`
- **Output**: Pass/fail results for each tool

### **interactive_mcp_tester.py** - Menu-Driven Tool Tester  
- **Purpose**: Test individual tools with custom parameters
- **Usage**: `python interactive_mcp_tester.py`
- **Features**: Interactive menu, custom JSON input, readable results

### **quick_demo.py** - Marketing Demo
- **Purpose**: Showcase all features with real examples
- **Usage**: `python quick_demo.py` 
- **Features**: Clean output, business-focused presentation

## 🧪 What the tools test:

1. **get_betting_matches** - Find matches available for analysis
2. **analyze_match_betting** - Comprehensive match predictions (main feature)
3. **get_team_form_analysis** - Team performance and momentum
4. **get_h2h_betting_analysis** - Historical matchup insights  
5. **get_league_value_bets** - Scan entire league for value bets

## 🚀 Quick Start:

```bash
# Install requirements
pip install -r requirements.txt

# Run automated tests
python test_remote_mcp.py

# Interactive testing
python interactive_mcp_tester.py

# Marketing demo
python quick_demo.py
```

## 🎯 What this proves:

- ✅ Your MCP server works 100% remotely on Railway
- ✅ All betting analysis tools are accessible via HTTPS  
- ✅ Zero local soccer code required
- ✅ Ready for Discord bot integration
- ✅ Subscribers can access from anywhere

## 🔧 Server Details:

- **URL**: `https://soccermcp-production.up.railway.app`
- **MCP Endpoint**: `https://soccermcp-production.up.railway.app/mcp`
- **Protocol**: JSON-RPC 2.0 (MCP compatible)
- **Tools**: 5 comprehensive betting analysis functions
- **Auth**: Secure SoccerDataAPI integration

## 🎉 Business Ready:

These testing tools prove your Enhanced Soccer Betting Analyzer is:
- **Production-ready** for subscribers
- **Scalable** across multiple Discord servers  
- **Professional** with clean, actionable output
- **Valuable** with comprehensive betting insights