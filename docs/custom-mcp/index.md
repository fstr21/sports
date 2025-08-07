# Sports AI MCP Documentation Index
## Complete Guide to Your Custom Sports Analysis Server

**Server:** `sports-ai`  
**Status:** ✅ Production Ready  
**Success Rate:** 86.2% data availability  

---

## 📚 **Documentation Overview**

### **🚀 [Getting Started - README](README.md)**
**Start here!** Complete overview of your Sports AI MCP including:
- What it does and why it's powerful
- Available tools and parameters
- Quick start guide and configuration
- Advanced usage patterns

### **📊 [Data Availability Reference](data-availability.md)**
**Essential reference** showing exactly what data you can get:
- Live game data examples (86.2% success rate)
- Team information and player stats
- News and injury reports
- Limitations and workarounds

### **🎯 [Example Queries](example-queries.md)**
**Practical examples** for real-world usage:
- WNBA and NFL analysis examples
- Betting-focused queries
- Custom sports analysis patterns
- Advanced scenarios and use cases

### **🔧 [ESPN Endpoints Reference](espn-endpoints.md)**
**Complete technical reference** of all available data:
- Every endpoint your MCP can access
- Data structures and field definitions
- Availability by sport and league
- Technical specifications

### **✅ [Verified Data Examples](verified-data-examples.md)**
**Real data samples** from actual API testing:
- Completed game data (Aug 3, 2025)
- Live game data (Aug 7, 2025)
- Team profiles and news examples
- Actual success rates and limitations

### **🆘 [Troubleshooting Guide](troubleshooting.md)**
**Problem-solving resource** for common issues:
- Error messages and solutions
- Performance optimization tips
- Configuration troubleshooting
- Testing and debugging tools

---

## 🎯 **Quick Navigation**

### **I want to...**

**Get started quickly** → [README.md](README.md)  
**See what data is available** → [data-availability.md](data-availability.md)  
**Find example queries** → [example-queries.md](example-queries.md)  
**Look up specific endpoints** → [espn-endpoints.md](espn-endpoints.md)  
**See real data examples** → [verified-data-examples.md](verified-data-examples.md)  
**Fix a problem** → [troubleshooting.md](troubleshooting.md)  

### **I'm working on...**

**Betting analysis** → [example-queries.md#betting-scenarios](example-queries.md)  
**Fantasy sports** → [example-queries.md#nfl-analysis-examples](example-queries.md)  
**Live game tracking** → [data-availability.md#live-game-data](data-availability.md)  
**Injury monitoring** → [example-queries.md#injury-impact-analysis](example-queries.md)  
**Team research** → [example-queries.md#team-research-deep-dives](example-queries.md)  

---

## 🏆 **Key Features Highlighted**

### **✅ What Your MCP Excels At:**
- **AI-Powered Analysis** - Uses OpenRouter for intelligent insights
- **Multi-Sport Coverage** - WNBA, NFL, NBA, MLB, NHL support
- **Betting Intelligence** - Specialized prompts for betting analysis
- **Real-Time Data** - Live ESPN API integration
- **Flexible Queries** - Custom prompts for any analysis need

### **⚠️ Important Limitations:**
- **No Live Betting Lines** - ESPN API doesn't provide live odds
- **Current Season Only** - Historical data limited
- **Rate Limits** - Both ESPN and OpenRouter have usage limits

---

## 🔧 **Technical Specifications**

### **Server Details**
- **Name:** `sports-ai`
- **File:** `mcp/sports_ai_mcp.py`
- **Language:** Python
- **Dependencies:** httpx, python-dotenv, mcp

### **Configuration Files**
- **Kiro:** `.kiro/settings/mcp.json`
- **Claude:** `.claude/mcp.json`
- **Environment:** `.env.local`

### **Available Tools**
1. **`analyzeWnbaGames`** - WNBA-specific analysis
2. **`analyzeNflGames`** - NFL-specific analysis  
3. **`customSportsAnalysis`** - Flexible multi-sport analysis

---

## 📈 **Performance Metrics**

### **Data Availability**
- **Overall Success Rate:** 86.2% (94/109 data points)
- **Live Game Data:** 100% available
- **Team Information:** 100% available
- **News & Injuries:** 87% available
- **Betting Lines:** 0% available (ESPN limitation)

### **Response Times**
- **Simple Queries:** 1-5 seconds
- **Complex Analysis:** 10-30 seconds
- **Multi-Game Analysis:** 15-45 seconds

---

## 🎓 **Learning Path**

### **Beginner**
1. Read [README.md](README.md) for overview
2. Try examples from [example-queries.md](example-queries.md)
3. Check [troubleshooting.md](troubleshooting.md) if issues arise

### **Intermediate**
1. Explore [data-availability.md](data-availability.md) for capabilities
2. Use [espn-endpoints.md](espn-endpoints.md) for technical details
3. Review [verified-data-examples.md](verified-data-examples.md) for real data

### **Advanced**
1. Create custom analysis workflows
2. Optimize queries for performance
3. Integrate with external betting APIs
4. Build automated analysis pipelines

---

## 🔄 **Updates and Maintenance**

### **Last Updated:** August 6, 2025
### **Version:** 1.0
### **Next Review:** As needed based on ESPN API changes

### **Changelog**
- **v1.0** - Initial documentation suite
- **v1.0** - Verified data examples from real games
- **v1.0** - Complete troubleshooting guide

---

**Need help?** Start with the [README](README.md) or jump to [troubleshooting](troubleshooting.md) if you're having issues!