# Sports Endpoints Development Plan
**Complete roadmap for expanding Sports AI MCP to support all major sports**

---

## 🎯 **Current Status**

### **✅ Working (Production Ready)**
- **WNBA** - Full integration with player names, statistics, and AI analysis
- **Eastern timezone handling** - Proper date/time management
- **OpenRouter integration** - AI-powered analysis and recommendations
- **Wagyu Sports MCP** - Live betting odds integration

### **⚠️ Partially Working (Needs Testing)**
- **NFL** - Function exists (`analyze_nfl_games`) but untested in integration
- **Custom Sports Analysis** - Generic function that should handle any sport

### **❌ Not Working (Needs Development)**
- **MLB** - Detected but returns 400 error (malformed URL)
- **NBA** - Not implemented
- **NHL** - Not implemented
- **College Sports** - Not implemented

---

## 🛠️ **Development Phases**

### **Phase 1: Fix MLB Support (Priority 1)**
**Goal**: Get MLB working like WNBA

#### **Tasks:**
1. **Fix URL Construction**
   - Current: `baseball_mlb/wnba/scoreboard` (wrong)
   - Should be: `baseball/mlb/scoreboard`

2. **Update Integration Test**
   - Add MLB handling in `test/mcp_integration_test.py`
   - Use `custom_sports_analysis` for MLB
   - Test with real MLB games

3. **Add MLB-Specific Function (Optional)**
   - Create `analyze_mlb_games()` similar to `analyze_wnba_games()`
   - Include pitcher matchups, ballpark factors
   - Player leaders for hitting/pitching

#### **Files to Modify:**
- `test/mcp_integration_test.py` - Add MLB sport handling
- `mcp/sports_ai_mcp.py` - Fix endpoint construction or add MLB function

#### **Testing:**
```bash
# Test MLB functionality
python test/mcp_integration_test.py
# Ask: "What MLB games are scheduled for today?"
```

### **Phase 2: Test & Fix NFL Support (Priority 2)**
**Goal**: Verify NFL integration works end-to-end

#### **Tasks:**
1. **Test Existing NFL Function**
   - Verify `analyze_nfl_games()` works with ESPN API
   - Check player data extraction
   - Test with integration script

2. **Add NFL to Integration Test**
   - Update sport detection logic
   - Add NFL-specific handling
   - Test with real NFL games (when season starts)

3. **Enhance NFL Analysis**
   - Add quarterback matchups
   - Include injury reports
   - Weather factors for outdoor games

#### **Files to Modify:**
- `test/mcp_integration_test.py` - Add NFL sport handling
- `mcp/sports_ai_mcp.py` - Enhance NFL analysis if needed

#### **Testing:**
```bash
# Test NFL functionality (during NFL season)
python test/mcp_integration_test.py
# Ask: "What are the best NFL bets for this week?"
```

### **Phase 3: Add NBA Support (Priority 3)**
**Goal**: Full NBA integration with player stats and betting analysis

#### **Tasks:**
1. **Create NBA Function**
   - Add `analyze_nba_games()` to Sports AI MCP
   - Include player leaders, team records
   - Handle NBA-specific analysis

2. **NBA-Specific Features**
   - Player prop predictions
   - Injury impact analysis
   - Back-to-back game considerations
   - Home/away performance splits

3. **Integration Testing**
   - Add NBA to integration test
   - Test with live NBA games
   - Verify betting odds integration

#### **Files to Create/Modify:**
- `mcp/sports_ai_mcp.py` - Add `analyze_nba_games()`
- `test/mcp_integration_test.py` - Add NBA handling
- `test/debug_nba.py` - NBA-specific testing script

### **Phase 4: Add NHL Support (Priority 4)**
**Goal**: Hockey analysis with goalie matchups and special teams

#### **Tasks:**
1. **Create NHL Function**
   - Add `analyze_nhl_games()` to Sports AI MCP
   - Include goalie stats, power play units
   - Handle hockey-specific metrics

2. **NHL-Specific Features**
   - Goalie matchup analysis
   - Power play vs penalty kill
   - Home ice advantage
   - Back-to-back considerations

3. **Integration Testing**
   - Add NHL to integration test
   - Test during NHL season
   - Verify puck line and totals analysis

### **Phase 5: College Sports (Priority 5)**
**Goal**: Support for major college sports (NCAAF, NCAAB)

#### **Tasks:**
1. **College Football (NCAAF)**
   - Add college football endpoint
   - Handle different data structure
   - Include conference considerations

2. **College Basketball (NCAAB)**
   - March Madness support
   - Conference tournament analysis
   - Seed-based predictions

---

## 📋 **Implementation Checklist**

### **For Each New Sport:**

#### **1. ESPN API Research**
- [ ] Identify correct ESPN endpoint
- [ ] Test API response structure
- [ ] Document available data fields
- [ ] Check player leader availability

#### **2. Sports AI MCP Development**
- [ ] Add sport-specific function (e.g., `analyze_mlb_games`)
- [ ] Implement player data extraction
- [ ] Add sport-specific analysis prompts
- [ ] Handle timezone and date formatting

#### **3. Integration Test Updates**
- [ ] Add sport to intent detection
- [ ] Add sport-specific handling logic
- [ ] Test with real games/data
- [ ] Verify error handling

#### **4. Wagyu Sports MCP Integration**
- [ ] Verify sport is supported by The Odds API
- [ ] Test betting odds retrieval
- [ ] Check market availability (spreads, totals, etc.)
- [ ] Validate odds format

#### **5. Testing & Validation**
- [ ] Create sport-specific debug script
- [ ] Test with live games
- [ ] Verify player names (not generic descriptions)
- [ ] Test betting integration
- [ ] Validate AI analysis quality

---

## 🔧 **Technical Implementation Details**

### **ESPN API Endpoints by Sport**
```
WNBA:  /basketball/wnba/scoreboard     ✅ Working
NFL:   /football/nfl/scoreboard        ⚠️ Needs testing
MLB:   /baseball/mlb/scoreboard        ❌ Broken URL
NBA:   /basketball/nba/scoreboard      ❌ Not implemented
NHL:   /hockey/nhl/scoreboard          ❌ Not implemented
NCAAF: /football/college-football/scoreboard  ❌ Not implemented
NCAAB: /basketball/mens-college-basketball/scoreboard  ❌ Not implemented
```

### **The Odds API Sport Keys**
```
WNBA:  basketball_wnba     ✅ Working
NFL:   americanfootball_nfl    ⚠️ Needs testing
MLB:   baseball_mlb        ❌ Needs fixing
NBA:   basketball_nba      ❌ Not implemented
NHL:   icehockey_nhl       ❌ Not implemented
NCAAF: americanfootball_ncaaf  ❌ Not implemented
NCAAB: basketball_ncaab    ❌ Not implemented
```

### **Code Structure Pattern**
Each sport should follow this pattern:

```python
@server.tool(
    name="analyzeSportGames",
    description="Fetch [SPORT] games and provide AI-powered analysis"
)
async def analyze_sport_games(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # 1. Parse arguments and set defaults
    # 2. Handle Eastern timezone dates
    # 3. Fetch ESPN data
    # 4. Extract player leaders
    # 5. Create sport-specific analysis prompt
    # 6. Send to OpenRouter for AI analysis
    # 7. Return structured response
```

---

## 🧪 **Testing Strategy**

### **Development Testing**
1. **Unit Tests** - Test each sport function individually
2. **Integration Tests** - Test with real API data
3. **Error Handling** - Test with invalid dates, missing games
4. **Performance Tests** - Monitor API response times

### **Debug Scripts to Create**
```
test/debug_mlb.py          # MLB-specific testing
test/debug_nfl.py          # NFL-specific testing  
test/debug_nba.py          # NBA-specific testing
test/debug_nhl.py          # NHL-specific testing
test/debug_all_sports.py   # Test all sports at once
```

### **Test Questions by Sport**
```
MLB: "Who will hit the most home runs in tonight's games?"
NFL: "What are the best over/under bets for this week's games?"
NBA: "Which player props have the best value tonight?"
NHL: "Who are the starting goalies and which games favor the over?"
```

---

## 📅 **Development Timeline**

### **Week 1: MLB Fix**
- Day 1-2: Fix MLB URL construction and test basic functionality
- Day 3-4: Add MLB to integration test and verify player data
- Day 5: Test with live MLB games and betting odds

### **Week 2: NFL Testing**
- Day 1-2: Test existing NFL function with real data
- Day 3-4: Add NFL to integration test
- Day 5: Enhance NFL analysis with football-specific insights

### **Week 3: NBA Implementation**
- Day 1-3: Create NBA function and player data extraction
- Day 4-5: Add NBA to integration test and verify functionality

### **Week 4: NHL Implementation**
- Day 1-3: Create NHL function with hockey-specific features
- Day 4-5: Add NHL to integration test and test with live games

### **Week 5: College Sports**
- Day 1-3: Research college sports API structure
- Day 4-5: Implement NCAAF and NCAAB basic functionality

---

## 🚨 **Risk Mitigation**

### **Don't Break Working WNBA**
- Always test WNBA functionality after changes
- Keep WNBA code path separate from new sports
- Use feature flags for new sports during development

### **API Rate Limits**
- Monitor ESPN API usage during testing
- Implement caching for repeated requests
- Use test mode for Wagyu Sports MCP during development

### **Data Quality**
- Verify player names (not generic descriptions) for each sport
- Test with multiple games to ensure consistency
- Handle edge cases (postponed games, no data available)

---

## 📊 **Success Metrics**

### **For Each Sport Implementation:**
- [ ] Returns actual player names (not "Team's leading scorer")
- [ ] Provides specific statistics (PPG, RPG, etc.)
- [ ] Integrates with betting odds successfully
- [ ] Gives actionable AI analysis
- [ ] Handles errors gracefully
- [ ] Maintains consistent response format

### **Overall System Goals:**
- Support 5+ major sports by end of development
- <2 second response time for most queries
- >95% uptime for API integrations
- Detailed logging for troubleshooting
- User-friendly error messages

---

## 🎯 **Next Steps**

### **Tomorrow's Tasks:**
1. **Start with MLB fix** - Highest priority, easiest to implement
2. **Create `test/debug_mlb.py`** - Dedicated MLB testing script
3. **Test `custom_sports_analysis`** - See if it works for MLB
4. **Document findings** - Update this plan based on results

### **Commands to Run:**
```bash
# Test current MLB issue
python test/mcp_integration_test.py
# Ask: "What MLB games are today?"

# Create MLB debug script
python test/debug_mlb.py

# Test custom sports analysis directly
python -c "from mcp.sports_ai_mcp import custom_sports_analysis; print(custom_sports_analysis({'sport': 'baseball', 'league': 'mlb'}))"
```

---

**🚀 This plan will transform your sports MCP from WNBA-only to a comprehensive multi-sport betting analysis system!**