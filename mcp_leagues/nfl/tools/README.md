# NFL MCP Testing Tools

Complete testing suite for the NFL MCP server deployed at `nflmcp-production.up.railway.app`.

## 🧪 **Test Scripts Overview**

### **Individual Tests**

#### **1. test_schedule.py**
**Purpose**: Test NFL schedule functionality
- ✅ Week 1 games (16 games expected)
- ✅ Full 2025 season (272 games)
- ✅ Team-specific schedules
- ✅ Playoff games
- ✅ Built-in betting odds validation

**Expected Results**: Complete NFL schedule with betting context

#### **2. test_teams.py** 
**Purpose**: Test NFL teams and divisions
- ✅ All 32 NFL teams
- ✅ AFC/NFC conferences (16 teams each)
- ✅ 8 divisions (4 teams each)
- ✅ Team metadata (colors, logos)

**Expected Results**: Complete team database with divisions

#### **3. test_player_stats.py**
**Purpose**: Test player statistics
- ✅ 2024 passing leaders
- ✅ 2024 rushing leaders  
- ✅ 2024 receiving leaders
- ✅ Team-specific stats
- ✅ Player search functionality

**Expected Results**: Comprehensive player performance data

#### **4. test_injuries.py**
**Purpose**: Test injury reports
- ✅ Current injury status
- ✅ Players Out/Questionable
- ✅ Team-specific injuries
- ✅ Position-specific injuries

**Expected Results**: Up-to-date injury reporting

#### **5. test_nfl_odds_integration.py**
**Purpose**: Test integration with Odds MCP
- ✅ NFL schedule from NFL MCP
- ✅ NFL odds from Odds MCP
- ✅ Game matching between MCPs
- ✅ Player props integration

**Expected Results**: Seamless cross-MCP functionality

### **Comprehensive Testing**

#### **run_all_tests.py**
**Purpose**: Execute all tests in sequence
- Runs all 5 test scripts automatically
- Generates comprehensive summary
- Provides Week 1 readiness assessment
- Exports complete test results

## 🚀 **How to Run Tests**

### **Individual Test**
```bash
cd C:\Users\fstr2\Desktop\sports\mcp_leagues\nfl\tools
python test_schedule.py
```

### **All Tests**
```bash
cd C:\Users\fstr2\Desktop\sports\mcp_leagues\nfl\tools
python run_all_tests.py
```

### **Prerequisites**
- Python 3.7+ with asyncio support
- httpx library for HTTP requests
- Access to deployed NFL MCP server

## 📊 **Test Results**

### **Success Criteria**

#### **Critical Tests (Must Pass)**
- ✅ **test_schedule.py**: NFL schedule with 272 games
- ✅ **test_nfl_odds_integration.py**: Odds MCP integration

#### **Important Tests (Should Pass)**
- ✅ **test_teams.py**: 32 teams in 8 divisions
- ✅ **test_player_stats.py**: 2024 player statistics
- ✅ **test_injuries.py**: Current injury reports

### **Expected Performance**
- **Response times**: < 500ms for most queries
- **Data accuracy**: 99%+ for game information
- **Integration success**: Game matching between MCPs
- **Error handling**: Graceful failure with detailed messages

## 📁 **Output Files**

Each test generates a JSON results file:
- `schedule_test_results_YYYYMMDD_HHMMSS.json`
- `teams_test_results_YYYYMMDD_HHMMSS.json` 
- `player_stats_test_results_YYYYMMDD_HHMMSS.json`
- `injuries_test_results_YYYYMMDD_HHMMSS.json`
- `nfl_odds_integration_results_YYYYMMDD_HHMMSS.json`

### **JSON Structure**
```json
{
  "timestamp": "2025-08-15T...",
  "server_url": "https://nflmcp-production.up.railway.app/mcp",
  "tests": {
    "test_name": {
      "success": true,
      "raw_data": {...}
    }
  },
  "summary": {
    "status": "SUCCESS",
    "successful_tests": 5,
    "total_tests": 5
  }
}
```

## 🎯 **Week 1 Preparation**

### **Pre-Season Testing (Now - Aug 31)**
1. **Validate all tools** with historical data
2. **Test integration** with Odds MCP
3. **Performance benchmarking**
4. **Error handling verification**

### **Week 1 Monitoring (Sept 1-8)**
1. **Daily test runs** to ensure readiness
2. **Real-time validation** during games
3. **Performance monitoring** under load
4. **Issue response** procedures

### **Success Metrics for Week 1**
- ✅ **16 Week 1 games** fully covered
- ✅ **Betting odds** from multiple sources
- ✅ **Injury reports** within 2 hours of updates
- ✅ **99.9% uptime** during game days

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Connection Errors**
```
[!] Request failed: Connection error
```
**Solution**: Verify NFL MCP server is running at `nflmcp-production.up.railway.app`

#### **MCP Errors**
```
[!] MCP Error: Unknown tool
```
**Solution**: Check tool name spelling and server deployment

#### **Empty Results**
```
[!] No data returned
```
**Solution**: Verify season parameter (2025 for schedule, 2024 for historical stats)

#### **Timeout Errors**
```
[!] Request timeout
```
**Solution**: Increase timeout or check server performance

### **Debug Mode**
Add debug output to any test:
```python
# Add at top of test script
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 **Performance Monitoring**

### **Key Metrics to Track**
- **Response Time**: Target < 500ms
- **Success Rate**: Target 99%+
- **Data Freshness**: Injury reports < 2 hours old
- **Integration Success**: Game matching rate > 90%

### **Load Testing**
For high-traffic scenarios:
```bash
# Run multiple concurrent tests
python test_schedule.py &
python test_teams.py &
python test_player_stats.py &
wait
```

## 🔗 **Integration Points**

### **With Odds MCP**
- **NFL schedule** provides game context
- **Odds MCP** provides enhanced betting markets
- **Team matching** enables cross-referencing
- **Player props** combine stats with betting lines

### **With Other MCPs**
- **MLB MCP**: Multi-sport platform
- **Soccer MCP**: International sports coverage
- **Combined analytics** across all sports

## 📋 **Test Schedule**

### **Daily Testing (Recommended)**
```bash
# Quick validation (5 minutes)
python test_schedule.py

# Full validation (15 minutes)  
python run_all_tests.py
```

### **Pre-Game Testing**
Before each NFL game day:
1. Run schedule test for current week
2. Verify injury report updates
3. Test odds integration
4. Monitor server health

### **Weekly Full Testing**
Every Monday during NFL season:
1. Complete test suite execution
2. Performance analysis
3. Data accuracy validation
4. Integration verification

## 🎯 **Next Steps**

### **After Successful Testing**
1. **Monitor** real-time performance during Week 1
2. **Optimize** based on actual usage patterns
3. **Enhance** with additional features
4. **Scale** for increased traffic

### **If Tests Fail**
1. **Identify** specific failure points
2. **Debug** server or configuration issues
3. **Fix** and re-test
4. **Validate** before Week 1 games

## 📞 **Support Resources**

### **Server Information**
- **URL**: `https://nflmcp-production.up.railway.app`
- **Health Check**: `https://nflmcp-production.up.railway.app/health`
- **Documentation**: `/README.md`

### **Related MCPs**
- **Odds MCP**: `https://odds-mcp-v2-production.up.railway.app`
- **Soccer MCP**: `https://soccermcp-production.up.railway.app`
- **MLB MCP**: `https://mlbmcp-production.up.railway.app`

---

**NFL MCP Testing Suite - Ready for 2025 Season! 🏈**