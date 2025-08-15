# Soccer MCP Test Scripts

Test scripts for validating Soccer MCP functionality with **EPL (Premier League)** and **La Liga** data access.

## 🎯 Purpose

These scripts test your **deployed Soccer MCP server** to ensure all tools work correctly with your Football-Data.org API plan that includes EPL and La Liga access.

## 📋 Available Test Scripts

### 1. `competitions_test.py`
**Tests**: `getCompetitions` tool  
**Purpose**: Verify access to EPL and La Liga competitions  
**Key Checks**:
- ✅ EPL (Premier League) accessible
- ✅ La Liga (Primera División) accessible  
- ✅ API key working correctly
- ✅ Competition metadata complete

### 2. `matches_test.py`
**Tests**: `getCompetitionMatches` tool  
**Purpose**: Get current and upcoming fixtures for both leagues  
**Key Checks**:
- ✅ Today's fixtures
- ✅ Next 7 days fixtures
- ✅ Specific matchday fixtures
- ✅ Match data completeness (teams, dates, status)

### 3. `standings_test.py`
**Tests**: `getCompetitionStandings` tool  
**Purpose**: Get current league tables for EPL and La Liga  
**Key Checks**:
- ✅ Current season standings
- ✅ League table with positions, points, goals
- ✅ Team rankings and statistics
- ✅ Season information

### 4. `team_matches_test.py`
**Tests**: `getTeamMatches` tool  
**Purpose**: Get fixtures for specific teams  
**Target Teams**:
- **EPL**: Arsenal, Chelsea, Manchester City, Liverpool
- **La Liga**: Real Madrid, Barcelona, Atlético Madrid, Sevilla  
**Key Checks**:
- ✅ Find team IDs from competition data
- ✅ Recent team matches
- ✅ Upcoming team fixtures
- ✅ Home/away match breakdown

## 🚀 How to Run Tests

### Prerequisites
1. **Deploy your Soccer MCP** to Railway
2. **Get your deployment URL** (e.g., `https://your-soccer-mcp.up.railway.app/mcp`)
3. **Update server URLs** in each test script
4. **Ensure Football-Data.org API key** is configured

### Update Server URLs
Before running, update this line in each script:
```python
self.server_url = "https://your-soccer-mcp.up.railway.app/mcp"  # TODO: Update with actual URL
```

### Run Individual Tests
```bash
# Test competitions access
python competitions_test.py

# Test match fixtures  
python matches_test.py

# Test league standings
python standings_test.py

# Test team-specific matches
python team_matches_test.py
```

### Run All Tests
```bash
# Windows
for %f in (*.py) do python "%f"

# PowerShell  
Get-ChildItem *.py | ForEach-Object { python $_.Name }
```

## 📊 Test Results

Each test creates a JSON results file with timestamp:
- `competitions_test_results_YYYYMMDD_HHMMSS.json`
- `matches_test_results_YYYYMMDD_HHMMSS.json`
- `standings_test_results_YYYYMMDD_HHMMSS.json`
- `team_matches_test_results_YYYYMMDD_HHMMSS.json`

### Result Structure
```json
{
  "timestamp": "2025-08-15T12:00:00",
  "summary": {
    "status": "SUCCESS|PARTIAL|FAILED",
    "details": "..."
  },
  "tests": {
    "test_name": {
      "success": true,
      "raw_data": {...}
    }
  }
}
```

## 🔍 Expected Results

### ✅ SUCCESS Indicators
- **Competitions**: Both EPL and La Liga found
- **Matches**: Fixtures returned for both leagues
- **Standings**: Complete league tables with 20 teams each
- **Team Matches**: Target teams found and fixtures retrieved

### ⚠️ PARTIAL Indicators  
- Only one league working (EPL or La Liga)
- Some tools working, others failing
- Limited data returned

### ❌ FAILURE Indicators
- API key issues (401/403 errors)
- No data returned
- Server connection failures
- Neither league accessible

## 🛠️ Troubleshooting

### Common Issues

**"No data returned"**
- Check server URL is correct
- Verify Soccer MCP is deployed and running
- Check Railway logs for errors

**"API key not configured"**
- Add `FOOTBALL_DATA_API_KEY` environment variable in Railway
- Verify API key is valid on Football-Data.org

**"EPL/La Liga not found"**
- Your API plan may not include these leagues
- Check Football-Data.org dashboard for plan details
- Verify competition IDs (PL=Premier League, PD=La Liga)

**"Request failed"**
- Check internet connection
- Verify Soccer MCP server is running
- Check for Railway deployment issues

### Debug Steps
1. **Test health endpoint**: `https://your-soccer-mcp.up.railway.app/`
2. **Check Railway logs** for deployment errors
3. **Run with test mode first** (`use_test_mode: true`)
4. **Verify API quota** on Football-Data.org dashboard

## 📈 Performance Notes

- **API Rate Limits**: 10 requests/minute (free tier)
- **Test Duration**: ~2-5 minutes per script
- **Data Volume**: Small JSON responses (typically < 50KB each)
- **Quota Usage**: Each test uses ~5-15 API calls

## 🎯 Next Steps

After successful testing:
1. **Integrate with Claude Code** using your Soccer MCP URL
2. **Create additional tools** for top scorers, match details, etc.
3. **Expand to more teams** as needed
4. **Add scheduling** for regular data updates

## 📝 Notes

- Scripts are designed to be **safe and non-destructive**
- All tests include **mock data mode** for development
- Results are **automatically timestamped** and saved
- Scripts follow the **same pattern as MLB tests** for consistency