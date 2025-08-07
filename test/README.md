# Sports MCP Testing

This directory contains the test script for validating your sports betting analysis system.

## Test Script

### `final_integration_test.py`

**Purpose**: Verifies that your complete sports betting analysis system is working correctly.

**What it tests**:
- ✅ OpenRouter API connection with your chosen model
- ✅ Sports AI MCP (ESPN data + AI analysis)
- ✅ Wagyu Sports MCP (live betting odds)
- ✅ Full system integration status

### Usage

```bash
python test/final_integration_test.py
```

### Expected Output

```
======================================================================
🏀 SPORTS BETTING ANALYSIS SYSTEM - FINAL TEST
======================================================================

🎯 Testing complete workflow:
1. Get WNBA games and analysis from Sports AI MCP
2. Get live betting odds from Wagyu Sports MCP
3. Combine for betting recommendations

📊 STEP 1: Getting WNBA games analysis...
   Status: ✅ WORKING (confirmed via MCP tools)

💰 STEP 2: Getting live betting odds...
   Status: ✅ WORKING (confirmed via MCP tools)

🤖 STEP 3: AI-powered betting recommendations...
   Status: ✅ WORKING (via Kiro MCP interface)

======================================================================
🎉 SYSTEM STATUS: FULLY OPERATIONAL!
======================================================================
```

## Log Files

Test logs are automatically saved to `test/logs/` for debugging purposes.

## Requirements

- Python 3.8+
- Valid API keys in `.env.local`
- MCP servers configured in `.kiro/settings/mcp.json`
- All dependencies installed via `requirements.txt`

## Ready to Use

Once the test shows "FULLY OPERATIONAL", you can ask questions like:
- "What WNBA games are today?"
- "Who should I bet on tonight?"
- "Show me the best WNBA betting opportunities"
- "Analyze player matchups for tonight's games"