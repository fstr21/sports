# Sports Betting Tips App - Product Requirements Document (PRD)

**Version:** 2.0  
**Date:** August 2025  
**Author:** [Your Name]  
**Status:** Updated for MCP Integration

---

## **1. EXECUTIVE SUMMARY**

### **Product Vision**
Build a data-driven sports betting analysis platform powered by **Model Context Protocol (MCP) servers** that provides actionable insights and predictions to help users make more informed betting decisions across major sports leagues.

### **Problem Statement**
Sports bettors struggle to find reliable, data-backed analysis that goes beyond surface-level tips. Most existing services either lack transparency in their methodology or charge premium prices without demonstrating consistent accuracy. Additionally, users want **interactive access** to the same analytical tools used by professionals.

### **Solution Overview**
A platform that combines real-time odds data with historical performance analytics through **intelligent MCP servers** and **OpenRouter LLM integration** to generate predictions and tips. Delivered through automated Discord posts with **premium MCP command access** for interactive analysis.

### **Success Criteria**
- Achieve >52% prediction accuracy across main bet types
- Build community of 100+ active Discord members within 3 months
- Generate $500/month recurring revenue by month 6 through **MCP premium subscriptions**
- Establish transparent track record of predictions and outcomes

---

## **2. TARGET USERS & USE CASES**

### **Primary User Personas**

#### **Persona 1: The Casual Bettor**
- **Demographics:** 25-35 years old, disposable income, bets for entertainment
- **Pain Points:** Overwhelmed by too much data, wants simple recommendations
- **Use Cases:** 
  - Get daily pick recommendations with clear reasoning
  - **NEW:** Ask simple questions like "What's the best bet tonight?"
  - Learn basic betting strategy through community discussion

#### **Persona 2: The Analytical Bettor**
- **Demographics:** 28-45 years old, has betting experience, wants an edge
- **Pain Points:** Time-consuming to analyze all games, needs consistent methodology
- **Use Cases:**
  - Access detailed statistical analysis and prediction models
  - **NEW:** Use MCP commands for custom analysis: "Compare Chiefs offense vs Bills defense"
  - Track long-term performance and ROI

#### **Persona 3: The Learning Enthusiast**
- **Demographics:** 22-40 years old, interested in sports analytics, may or may not bet
- **Pain Points:** Wants to understand prediction methodology, lacks technical skills
- **Use Cases:**
  - **NEW:** Interactive learning through MCP commands: "Why is this a good bet?"
  - Understand the math behind betting odds and value
  - Participate in educational discussions about sports performance

### **User Journey Map**
1. **Discovery:** User finds app through social media, Discord servers, or referrals
2. **Evaluation:** User joins free Discord tier, reviews historical accuracy
3. **Engagement:** User participates in daily tip discussions, asks questions
4. **Conversion:** User upgrades to premium for **MCP command access** and detailed analysis
5. **Retention:** User stays engaged through accurate tips and **interactive MCP tools**
6. **Advocacy:** User refers friends and provides feedback for improvements

---

## **3. CORE FEATURES & REQUIREMENTS**

### **3.1 MVP Features (Phase 1)**

#### **Discord Bot Core**
- **Automated Daily Analysis**
  - **NEW:** Single OpenRouter API call orchestrates all analysis
  - Automated posting of 3-5 daily picks at scheduled times
  - Format: Game, Pick, Confidence Level, AI-Generated Reasoning
  - Include relevant odds from major sportsbooks

- **Basic Commands**
  - `!tips` - Show today's active tips
  - `!record` - Display recent accuracy statistics
  - `!help` - List available commands and usage

#### **MCP Server Infrastructure (NEW)**
- **Core MCP Servers:**
  - `schedule_mcp.py` - Fetch daily game schedules
  - `odds_mcp.py` - Retrieve betting odds from APIs
  - `team_stats_mcp.py` - Get team performance data
  - `analysis_mcp.py` - Run calculations and prediction models
  - `discord_formatter_mcp.py` - Format posts for Discord

- **Intelligent Automation Pipeline:**
  ```python
  # Single automation script
  response = openrouter_client.create(
      messages=[{"role": "user", "content": 
          "Give me betting recommendations for all NFL games today, formatted for Discord"
      }]
  )
  # OpenRouter + Claude orchestrates all MCP servers automatically
  ```

#### **Basic Analytics**
- **Accuracy Tracking**
  - Win/loss record by sport and bet type
  - Overall accuracy percentage
  - Recent performance trends (last 7 days, 30 days)

### **3.2 Premium Features (Phase 2) - MCP Command Access**

#### **Premium MCP Server Access**

**Tier 1: Basic Analysis ($15/month)**
- Access to interactive MCP commands in dedicated Discord channels
- **Available Commands:**
  ```
  "What games are today?"
  "Show me [team] recent performance"
  "Get odds for [team1] vs [team2]"
  "What's your take on [specific bet]?"
  ```

**Tier 2: Advanced Analysis ($35/month)**
- All Tier 1 features plus advanced MCP commands
- **Advanced Commands:**
  ```
  "Find value bets in today's slate"
  "Compare [team1] offense vs [team2] defense"
  "What player props look good for [player]?"
  "Show me contrarian plays for Sunday"
  "Analyze weather impact on [game]"
  ```

**Tier 3: Professional Suite ($75/month)**
- All previous features plus professional-grade MCP tools
- **Professional Commands:**
  ```
  "Run custom betting model on today's games"
  "Backtest this strategy against last season"
  "Generate full betting card for weekend"
  "Compare my analysis to consensus"
  "Show me line movement alerts"
  ```

#### **Interactive Features**
- **Multi-Platform Access:** MCP servers work in Claude Code, Claude Desktop, Cursor
- **Persistent Context:** Commands remember previous analysis in conversation
- **Custom Alerts:** Set up automated notifications for specific teams/situations

### **3.3 Future Features (Phase 3+)**

#### **Web Dashboard**
- **MCP Integration Portal**
  - One-click MCP server setup for users' own AI clients
  - Historical analysis recreation through web interface
  - Custom MCP server configurations

#### **Expanded Sports Coverage**
- **Additional MCP Servers**
  - `nhl_analysis_mcp.py`
  - `nba_analysis_mcp.py`
  - `soccer_analysis_mcp.py`

---

## **4. TECHNICAL REQUIREMENTS**

### **4.1 Architecture Overview**

#### **Core Technology Stack**
- **Backend:** Python (FastMCP framework)
- **LLM Provider:** **OpenRouter API** (cost-effective, multi-model access)
- **MCP Servers:** Custom Python servers using FastMCP
- **Database:** PostgreSQL
- **Discord Integration:** discord.py library
- **Data Sources:** The Odds API, ESPN API, others TBD
- **Hosting:** Railway/Heroku (initial), AWS (scale)
- **Monitoring:** Basic logging and error tracking

#### **MCP-Based Architecture (NEW)**

**Automated Daily Pipeline:**
```
Single API Call → OpenRouter/Claude → Orchestrates All MCP Servers → Discord Posts
```

**MCP Server Organization:**
```
C:\Users\[USER]\Desktop\sports\
├── mcp\                           # All MCP servers
│   ├── schedule_mcp.py           # Game schedule fetching
│   ├── odds_mcp.py               # Betting odds retrieval  
│   ├── team_stats_mcp.py         # Team performance data
│   ├── analysis_mcp.py           # Calculations & predictions
│   └── discord_formatter_mcp.py  # Discord post formatting
├── automation\                   # Orchestration scripts
│   └── sunday_automation.py     # Single script calls OpenRouter
├── modules\                      # Shared logic modules
│   ├── data_fetchers\
│   ├── calculators\
│   └── database\
└── config\
    ├── mcp_config.json          # MCP server configurations
    └── openrouter_config.py     # API configurations
```

#### **Example MCP Server Implementation:**
```python
# mcp/analysis_mcp.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("betting-analysis")

@mcp.tool()
async def analyze_game_matchup(team1: str, team2: str, odds: str) -> str:
    """Analyze betting opportunities for a specific game"""
    # Your calculation logic here
    # Returns: "Chiefs -3 is good value because..."
    
@mcp.tool()
async def find_value_bets(games_data: str) -> str:
    """Find the best value bets across all games"""
    # Your value detection logic
    # Returns: "Top 3 value bets: Chiefs -3, OVER 47.5..."

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

#### **OpenRouter Integration:**
```python
# automation/sunday_automation.py
import requests

def generate_sunday_picks():
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    response = requests.post(url, 
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{
                "role": "user", 
                "content": "Give me betting recommendations for all NFL games today, formatted for Discord channels"
            }],
            "max_tokens": 2000
        }
    )
    
    # Claude automatically uses all MCP servers
    # Returns complete Discord posts ready to publish
    return response.json()['choices'][0]['message']['content']
```

### **4.2 Performance Requirements**
- **Response Time:** Discord commands respond within 2 seconds
- **MCP Commands:** Premium user commands respond within 5 seconds
- **OpenRouter Latency:** Account for 2-3 second API response times
- **Uptime:** 99% availability during peak betting hours
- **Data Freshness:** Odds updated every 15 minutes, predictions daily
- **Scalability:** Support 1000+ Discord users + 100+ premium MCP users

### **4.3 Security & Compliance**
- **API Key Management**
  - Secure OpenRouter API key storage
  - User-specific MCP server access controls
  - Rate limiting for premium MCP commands

- **Data Protection**
  - No storage of user betting activity or financial information
  - Secure user authentication for premium MCP access
  - Regular security updates and dependency management

---

## **5. SUCCESS METRICS & KPIs**

### **5.1 Product Metrics**
- **Prediction Accuracy**
  - Target: >52% overall accuracy by month 3
  - Target: >55% overall accuracy by month 6
  - Track MCP-generated vs traditional predictions

- **User Engagement**
  - Daily active Discord users
  - **NEW:** MCP command usage frequency per premium user
  - **NEW:** Average MCP session length
  - Message participation in tip discussions

### **5.2 Business Metrics**
- **Community Growth**
  - Total Discord members
  - **NEW:** Premium MCP subscriber count by tier
  - Monthly churn rate (<20% target)

- **Revenue**
  - Monthly recurring revenue (MRR) from MCP subscriptions
  - **NEW:** MCP tier upgrade rates
  - Customer lifetime value (CLV)
  - **NEW:** OpenRouter API cost optimization

### **5.3 Quality Metrics**
- **User Satisfaction**
  - **NEW:** MCP command accuracy and helpfulness ratings
  - Community feedback and sentiment
  - Feature request frequency

- **Technical Performance**
  - **NEW:** MCP server uptime and response times
  - **NEW:** OpenRouter API reliability
  - System uptime and reliability
  - Error rates and resolution times

---

## **6. LAUNCH STRATEGY & TIMELINE**

### **6.1 Development Phases**

#### **Phase 1: MCP MVP (Months 1-2)**
- Build core MCP servers (schedule, odds, stats, analysis, formatter)
- Implement OpenRouter integration for automation
- **NEW:** Replace 6-script pipeline with single intelligent automation
- Launch private beta with friends/family
- Test MCP server reliability and accuracy

#### **Phase 2: Premium MCP Launch (Month 3)**
- Implement premium MCP command access tiers
- **NEW:** Deploy MCP servers for user interaction
- Add advanced analysis MCP tools
- Launch marketing focused on **"AI-powered betting analysis tools"**
- Establish transparent accuracy reporting

#### **Phase 3: Scale & Expand (Months 4-6)**
- **NEW:** Additional sport-specific MCP servers
- Advanced MCP commands and features
- Multi-platform MCP access (Claude Code, Desktop, Cursor)
- **NEW:** Custom MCP server configurations for power users
- Revenue optimization and growth

### **6.2 Go-to-Market Strategy**
- **Initial Launch:** Friends, family, and personal network
- **Community Building:** Engage in existing sports betting Discord servers
- **Content Marketing:** Twitter/X showcasing **MCP command capabilities**
- **Referral Program:** Incentivize existing users to invite others
- **Partnerships:** Collaborate with sports content creators
- **NEW:** Developer Community: Open-source basic MCP servers to attract technical users

---

## **7. RISKS & MITIGATION**

### **7.1 Technical Risks**
- **OpenRouter API Reliability:** Backup LLM providers and graceful degradation
- **MCP Server Complexity:** Thorough testing and monitoring of server interactions
- **Prediction Accuracy:** Conservative accuracy claims and continuous model improvement
- **Scaling Issues:** Modular MCP architecture and performance monitoring

### **7.2 Business Risks**
- **MCP Adoption:** User education and clear value demonstration
- **API Costs:** Monitor OpenRouter usage and optimize pricing tiers
- **Legal/Regulatory:** Regular compliance review and legal consultation
- **Market Competition:** Focus on unique MCP-powered interactive features

### **7.3 Operational Risks**
- **MCP Server Dependencies:** Robust error handling and fallback mechanisms
- **Premium Support:** Responsive support for MCP command issues
- **Data Quality:** Multiple validation layers and anomaly detection

---

## **8. OUT OF SCOPE**

### **8.1 Explicitly Not Included**
- **Direct Betting Integration:** No facilitation of actual betting transactions
- **Licensed Sportsbook Operations:** No handling of real money
- **Guaranteed Profits:** No promises of winning or profit guarantees
- **Personal Financial Advice:** No individual betting strategy consultation
- **Custom MCP Development:** No building custom MCP servers for individual users (Phase 1)

### **8.2 Future Considerations**
- **Live Betting MCP:** Real-time in-game prediction MCP servers
- **AI/ML Enhancement:** Advanced machine learning MCP servers
- **Social MCP Features:** User-generated MCP commands and sharing
- **API Monetization:** Selling MCP server access to third parties

---

## **9. APPENDIX**

### **9.1 Technical Dependencies**
- **NEW:** OpenRouter API access and pricing
- **NEW:** MCP SDK and FastMCP framework
- Discord API and bot permissions
- External sports data APIs and pricing
- Database hosting and backup systems
- **NEW:** MCP server hosting and monitoring

### **9.2 Resource Requirements**
- **Development Time:** Estimated 60-80 hours for MCP MVP
- **Monthly Operating Costs:** $75-200 (APIs, hosting, OpenRouter usage, tools)
- **NEW:** OpenRouter API costs: ~$10-30/month for automation
- **NEW:** Premium MCP usage: ~$20-50/month additional
- **Tools and Software:** Development environment, MCP testing tools, monitoring

### **9.3 Compliance Checklist**
- [ ] Discord Terms of Service review
- [ ] **NEW:** OpenRouter Terms of Service compliance
- [ ] **NEW:** MCP server security and access controls
- [ ] Sports betting regulation research by state
- [ ] Data privacy policy creation (including MCP data handling)
- [ ] User age verification implementation
- [ ] Legal disclaimer development

---

**Document Status:** Updated for MCP Integration  
**Next Steps:** MCP server development and OpenRouter integration  
**Review Date:** [Date + 1 week]