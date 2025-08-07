# MCP Integration Tests

This directory contains test scripts for validating the integration between multiple MCP servers and external APIs.

## Test Scripts

### `mcp_integration_test.py`

Tests the integration between:
- **Sports AI MCP** - ESPN data and AI analysis
- **Wagyu Sports MCP** - Betting odds from The Odds API  
- **OpenRouter LLM** - AI-powered analysis and recommendations

#### Features

- **Interactive prompting** - Ask natural language questions about sports betting
- **Intent detection** - Automatically determines what data is needed
- **Dual MCP integration** - Calls both MCP servers as needed
- **Detailed logging** - Tracks data flow, API calls, and performance
- **Error handling** - Graceful handling of API failures
- **Log persistence** - Saves detailed logs to `test/logs/`

#### Usage

```bash
# Run the integration test
python test/mcp_integration_test.py

# Example questions to try:
# "Based on the odds for the WNBA games tomorrow can you tell me which spread bets to place and why?"
# "What are the best NBA moneyline bets for tonight's games?"
# "Analyze the NFL games this week and recommend totals bets"
```

#### Sample Output

```
================================================================================
MCP Integration Test - Sports AI + Wagyu Sports + OpenRouter
================================================================================

Enter your sports betting question: Based on the odds for the WNBA games tomorrow can you tell me which spread bets to place and why?

[14:23:15.123] [INFO] Starting MCP integration test...
[14:23:15.124] [INFO] User question: Based on the odds for the WNBA games tomorrow can you tell me which spread bets to place and why?
[14:23:15.125] [INFO] Analyzing user query for intent...
[14:23:15.126] [INFO] Query intent detected: {
  "sports": ["basketball_wnba"],
  "timeframe": "tomorrow",
  "bet_types": ["spreads"],
  "needs_odds": true,
  "needs_games": true,
  "needs_analysis": true
}
[14:23:15.127] [INFO] Calling Sports AI MCP...
[14:23:16.234] [INFO] Sports AI MCP returned data for 1 sports
[14:23:16.235] [INFO] Calling Wagyu Sports MCP...
[14:23:16.456] [INFO] Wagyu Sports MCP returned odds for 1 sports
[14:23:16.457] [INFO] Combining data from both MCPs...
[14:23:16.458] [INFO] Combined data length: 2847 characters
[14:23:16.459] [INFO] Sending query to OpenRouter LLM...
[14:23:16.460] [INFO] Sending 3124 characters to OpenRouter
[14:23:16.461] [INFO] Using model: openrouter/horizon-beta
[14:23:18.789] [INFO] OpenRouter response received in 2.33 seconds
[14:23:18.790] [INFO] Token usage - Prompt: 1247, Completion: 456, Total: 1703
[14:23:18.791] [INFO] OpenRouter returned 1834 characters

================================================================================
AI RESPONSE
================================================================================
Based on the WNBA games and betting odds provided, here are my spread betting recommendations:

[AI analysis would appear here...]
================================================================================

Test completed. Check test/logs/ for detailed logs.
```

#### Log Files

Detailed logs are saved to `test/logs/mcp_test_YYYYMMDD_HHMMSS.log` containing:
- Timestamp for each operation
- MCP call details and responses
- Data transformation steps
- OpenRouter API usage and costs
- Error messages and debugging info

#### Requirements

- Python 3.8+
- Both MCP servers configured in Kiro
- Valid API keys in `.env.local`:
  - `OPENROUTER_API_KEY`
  - `ODDS_API_KEY`
- Required Python packages (see main requirements.txt)

#### Troubleshooting

1. **MCP Connection Issues**: Check that both MCP servers are properly configured in `.kiro/settings/mcp.json`
2. **API Key Errors**: Verify all required keys are set in `.env.local`
3. **Import Errors**: Ensure you're running from the project root directory
4. **Rate Limits**: The script uses test mode by default to avoid API costs

#### Development Notes

- Currently uses mock data for Wagyu Sports MCP to avoid API costs during testing
- Sports AI MCP calls are made directly to the module functions
- Future versions will use proper MCP client protocol
- Logs are essential for debugging data flow between systems