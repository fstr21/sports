# Sports AI MCP Troubleshooting Guide
## Common Issues and Solutions

**Last Updated:** August 6, 2025  
**MCP Server:** `sports-ai`  
**File:** `mcp/sports_ai_mcp.py`

---

## 🚨 **Common Error Messages**

### **"OpenRouter API key not configured"**

**Cause:** Missing or incorrect OpenRouter API configuration

**Solutions:**
1. **Check `.env.local` file exists** in your project root
2. **Verify API key format:**
   ```
   OPENROUTER_API_KEY=sk-or-v1-[your-actual-key]
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=openrouter/horizon-beta
   ```
3. **Ensure no extra spaces or quotes** around the key
4. **Restart your MCP server** after making changes

### **"No game data available for any date"**

**Cause:** Invalid date format or no games on specified date

**Solutions:**
1. **Use correct date format:** YYYYMMDD (e.g., "20250807")
2. **Try current date or recent dates:**
   ```python
   analyzeWnbaGames({
       "dates": "20250807"  # Today's date
   })
   ```
3. **Remove date parameter** to get current games:
   ```python
   analyzeWnbaGames({
       "analysis_type": "betting"
   })
   ```
4. **Check if league is in season** (WNBA: April-October)

### **"dates must be a string in YYYYMMDD format"**

**Cause:** Incorrect date format provided

**Solutions:**
1. **Use string format:** `"20250807"` not `20250807`
2. **Use 8-digit format:** `"20250807"` not `"2025-08-07"`
3. **Example correct usage:**
   ```python
   analyzeWnbaGames({
       "dates": "20250803",  # Correct format
       "analysis_type": "betting"
   })
   ```

### **"limit must be a positive integer"**

**Cause:** Invalid limit parameter

**Solutions:**
1. **Use positive integers only:** `1, 2, 3, 5`
2. **Don't use decimals:** `3` not `3.5`
3. **Example correct usage:**
   ```python
   analyzeWnbaGames({
       "limit": 3,  # Correct
       "analysis_type": "betting"
   })
   ```

---

## 🔧 **Performance Issues**

### **Slow Response Times**

**Symptoms:** Queries taking 30+ seconds to complete

**Solutions:**
1. **Reduce scope of analysis:**
   ```python
   # Instead of analyzing all games
   analyzeWnbaGames({"analysis_type": "betting"})
   
   # Limit to specific games
   analyzeWnbaGames({
       "limit": 2,
       "analysis_type": "betting"
   })
   ```

2. **Use more specific prompts:**
   ```python
   # Instead of general analysis
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba",
       "endpoint": "scoreboard",
       "prompt": "Analyze all aspects of today's games"
   })
   
   # Be specific
   customSportsAnalysis({
       "sport": "basketball", 
       "league": "wnba",
       "endpoint": "scoreboard",
       "prompt": "Focus on point spread analysis for the Aces vs Valkyries game"
   })
   ```

3. **Check OpenRouter API status** at https://openrouter.ai/

### **Timeout Errors**

**Symptoms:** Requests failing with timeout messages

**Solutions:**
1. **Simplify your prompts** - Complex analysis takes longer
2. **Reduce number of games analyzed** using `limit` parameter
3. **Try again in a few minutes** - May be temporary API issues
4. **Check your internet connection**

---

## 📊 **Data Quality Issues**

### **Missing or Incomplete Data**

**Symptoms:** Analysis mentions missing information

**Solutions:**
1. **Try different endpoints:**
   ```python
   # If scoreboard data is incomplete, try news
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba", 
       "endpoint": "news",
       "prompt": "Get latest injury reports and team news"
   })
   ```

2. **Use multiple queries for comprehensive data:**
   ```python
   # Get team info
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba",
       "endpoint": "teams",
       "prompt": "Get team profiles and records"
   })
   
   # Then get game data
   analyzeWnbaGames({
       "analysis_type": "betting"
   })
   ```

3. **Check if games are live, completed, or scheduled** - Data availability varies

### **Outdated Information**

**Symptoms:** Analysis references old games or incorrect dates

**Solutions:**
1. **Use current dates** in your queries
2. **Specify recent date ranges:**
   ```python
   analyzeWnbaGames({
       "dates": "20250807",  # Today's date
       "analysis_type": "performance"
   })
   ```
3. **Check news endpoint for latest updates:**
   ```python
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba",
       "endpoint": "news",
       "prompt": "Get breaking news from the last 24 hours"
   })
   ```

---

## 🎯 **Analysis Quality Issues**

### **Generic or Unhelpful Analysis**

**Symptoms:** AI provides vague or general responses

**Solutions:**
1. **Use specific analysis types:**
   ```python
   # Instead of general
   analyzeWnbaGames({"analysis_type": "general"})
   
   # Use specific
   analyzeWnbaGames({"analysis_type": "betting"})
   ```

2. **Provide detailed custom prompts:**
   ```python
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba",
       "endpoint": "scoreboard",
       "prompt": "Analyze the Las Vegas Aces vs Golden State Valkyries game focusing on point spread value, key player matchups, and recent form trends"
   })
   ```

3. **Ask for specific recommendations:**
   ```python
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba", 
       "endpoint": "scoreboard",
       "prompt": "Provide specific betting recommendations with reasoning for tonight's games including spreads, totals, and best value plays"
   })
   ```

### **Analysis Doesn't Match Request**

**Symptoms:** AI analyzes wrong games or provides irrelevant information

**Solutions:**
1. **Be more specific in prompts:**
   ```python
   # Instead of
   "prompt": "Analyze the game"
   
   # Use
   "prompt": "Analyze the Las Vegas Aces at Golden State Valkyries game scheduled for tonight"
   ```

2. **Include context in your requests:**
   ```python
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba",
       "endpoint": "scoreboard",
       "prompt": "For today's WNBA games only, focus on betting analysis for point spreads and totals"
   })
   ```

---

## 🔌 **Connection Issues**

### **MCP Server Not Responding**

**Symptoms:** No response from MCP tools

**Solutions:**
1. **Check MCP configuration:**
   - Verify `.kiro/settings/mcp.json` has correct path
   - Ensure `sports-ai` server is enabled (`"disabled": false`)

2. **Restart MCP server:**
   - In Kiro: Restart the application
   - Check MCP server status in Kiro's MCP panel

3. **Verify file exists:**
   ```bash
   # Check if the MCP file exists
   ls mcp/sports_ai_mcp.py
   ```

4. **Test Python dependencies:**
   ```bash
   # Install required packages
   pip install httpx python-dotenv mcp
   ```

### **ESPN API Connection Issues**

**Symptoms:** "Failed to fetch data" or connection errors

**Solutions:**
1. **Check internet connection**
2. **Try again in a few minutes** - ESPN API may be temporarily down
3. **Use different endpoints:**
   ```python
   # If scoreboard fails, try teams
   customSportsAnalysis({
       "sport": "basketball",
       "league": "wnba",
       "endpoint": "teams",
       "prompt": "Get team information"
   })
   ```

---

## 🧪 **Testing and Debugging**

### **Test Basic Functionality**

**Simple test queries to verify everything works:**

```python
# Test 1: Basic WNBA analysis
analyzeWnbaGames({
    "analysis_type": "general"
})

# Test 2: Custom analysis
customSportsAnalysis({
    "sport": "basketball",
    "league": "wnba",
    "endpoint": "teams",
    "prompt": "List all WNBA teams"
})

# Test 3: News endpoint
customSportsAnalysis({
    "sport": "basketball", 
    "league": "wnba",
    "endpoint": "news",
    "prompt": "Get latest WNBA news"
})
```

### **Debug Data Availability**

**Use the ESPN data validator tool:**

```bash
# Run the validator to test current data availability
python espn_data_validator.py
```

This will test all endpoints and show you exactly what data is available.

---

## 📋 **Best Practices to Avoid Issues**

### **Query Construction**
1. **Start simple** - Test basic queries before complex ones
2. **Use specific dates** - YYYYMMDD format only
3. **Limit scope** - Use `limit` parameter for faster responses
4. **Be specific** - Detailed prompts get better results

### **Error Handling**
1. **Try alternative approaches** if one method fails
2. **Check multiple endpoints** for comprehensive data
3. **Use current dates** to avoid missing data
4. **Verify configuration** before complex debugging

### **Performance Optimization**
1. **Cache results** for completed games (data won't change)
2. **Use appropriate analysis types** for your needs
3. **Combine related queries** instead of many small ones
4. **Monitor API usage** to avoid rate limits

---

## 🆘 **Getting Additional Help**

### **Documentation Resources**
- [Main README](README.md) - Complete MCP overview
- [Data Availability](data-availability.md) - What data is available
- [Example Queries](example-queries.md) - Working examples
- [ESPN Endpoints](espn-endpoints.md) - Complete endpoint reference

### **Testing Tools**
- `espn_data_validator.py` - Test current data availability
- MCP Inspector - Debug MCP communication
- Kiro MCP panel - Check server status

### **Configuration Files**
- `.env.local` - OpenRouter API configuration
- `.kiro/settings/mcp.json` - Kiro MCP configuration
- `.claude/mcp.json` - Claude MCP configuration

---

## 📞 **Quick Reference Commands**

### **Test MCP Server**
```bash
# Test if Python dependencies are installed
python -c "import httpx, mcp; print('Dependencies OK')"

# Test if MCP file exists and runs
python mcp/sports_ai_mcp.py
```

### **Check Configuration**
```bash
# Verify .env.local exists
cat .env.local

# Check MCP configuration
cat .kiro/settings/mcp.json
```

### **Reset and Restart**
```bash
# If all else fails, restart everything
# 1. Close Kiro
# 2. Restart Kiro
# 3. Test with simple query
```

---

**Remember:** Most issues are configuration-related. Double-check your `.env.local` file and MCP configuration before diving into complex debugging!