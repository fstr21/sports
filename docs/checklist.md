
# Sports Betting App: Pre-Coding Research Checklist

_Complete this checklist BEFORE subscribing to any APIs or writing code_

---

## **🛠️ PROJECT SETUP & STEERING DOCUMENTS**

- [ ] **Research and install useful MCP (Model Context Protocol) tools**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **MCP Tools to Research:** Database MCP (PostgreSQL, SQLite, MySQL), Web scraping MCP, HTTP client MCP, File system MCP, Testing framework MCP, API documentation MCP, Git operations MCP, Docker management MCP
  - **Installation Strategy:** 
  - **Configuration Required:** 
  - **Notes:** Research MCP tools that could accelerate development for sports betting data collection, API interactions, database management, and testing workflows

- [ ] **Create steering documents for Claude Code and Kiro on project workflow**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Claude Code Instructions:** How to work with the project structure
  - **Kiro Instructions:** Project-specific guidance and preferences
  - **Workflow Documentation:** Development process and standards
  - **MCP Integration:** Ensure steering documents reference and utilize available MCP servers (httpx, sqlalchemy, prefect, zen, custom_normalization) for enhanced development capabilities
  - **Notes:** We will be using a library of known-to-work example scripts for each possible request. Scripts will be in this format:

Python

"""
NFL Schedule Fetching - Proof of Concept
========================================

Purpose: Test fetching NFL game schedule data
API: ESPN API
Cost: Free
Rate Limit: Unknown (test carefully)
Date Tested: [Date]
Status: ✅ Working | ⚠️ Needs Fix | ❌ Failed

Research Checklist Item: 
"Source for scheduled games for NFL with example code and date lookups"
"""

import requests
import json
from datetime import datetime, timedelta
import os

# Configuration
API_BASE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl"
SEASON = 2024
WEEK = 1

def fetch_nfl_schedule(season=SEASON, week=WEEK):
    """
    Fetch NFL schedule for specific season and week
    ```
LLM Steering Command - Code Generation and Architecture:
For all code generation tasks, you must strictly adhere to the Modular Step-Based Architecture outlined in the project's Product Requirements Document (PRD). Your primary directive is to maintain a clean separation between orchestration and business logic.

Core Principle: All processes must be implemented as a discrete, step-based pipeline.

Orchestration: Generate thin orchestrator scripts (runner scripts) located exclusively in the src/runners/ directory. These scripts are responsible only for coordinating the execution flow by calling logic modules in a sequence. They must not contain any business logic, complex data manipulation, or direct API interactions.

Logic: Generate "fat" logic modules located exclusively in the src/modules/ directory. All business logic, data processing, calculations, API client interactions, and database operations must be encapsulated within these modules.

Single Responsibility: Every script and module you create must have a single, clearly defined purpose. For example, one runner script executes a step, and one module contains the detailed logic for that step.

Testability and Independence: Design all modules to be independently executable and testable. The logic within a module should not depend on the orchestrator to function; it should be self-contained.

---

## **📊 DATA MAPPING & STANDARDIZATION**

### Team ID Mappings
- [ ] **NFL team name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **NHL team name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **NBA team name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **UEFA team name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **EPL team name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **La Liga team name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

### Player ID Mappings
- [ ] **NFL player name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **NHL player name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

- [ ] **NBA player name/id mapping across various sources**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sources Found:** 
  - **Mapping Strategy:** 
  - **Notes:** 

---

## **📅 GAME SCHEDULE DATA SOURCES**

- [ ] **Source for scheduled games for NFL with example code and date lookups**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Example Code:** 
  - **Rate Limits:** 
  - **Cost:** 
  - **Notes:** 

- [ ] **Source for scheduled games for NBA with example code and date lookups**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Example Code:** 
  - **Rate Limits:** 
  - **Cost:** 
  - **Notes:** 

- [ ] **Source for scheduled games for NHL with example code and date lookups**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Example Code:** 
  - **Rate Limits:** 
  - **Cost:** 
  - **Notes:** 

---

## **💰 ODDS & LINES DATA SOURCES**

- [ ] **Source of the USA team odds and lines**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Bookmakers Covered:** 
  - **Markets Available:** (ML, Spread, Totals)
  - **Update Frequency:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

- [ ] **Source of the player odds and lines**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Props Available:** 
  - **Sports Covered:** 
  - **Update Frequency:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

- [ ] **Source for team level odds and lines for major soccer leagues (UEFA, EPL, La Liga)**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Leagues Covered:** 
  - **Markets Available:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

---

## **📈 PERFORMANCE DATA SOURCES**

- [ ] **Source for NFL team level performances with example code**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Stats Available:** 
  - **Historical Depth:** 
  - **Update Frequency:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

- [ ] **Source for NHL team level performances with example code**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Stats Available:** 
  - **Historical Depth:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

- [ ] **Source for performances for UEFA, EPL, La Liga with example code**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Stats Available:** 
  - **Leagues Covered:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

---

## **🧮 PREDICTION CALCULATIONS & CODE**

### NFL Team Level Predictions
- [ ] **Source AND calculations for predictions with code for NFL team level ML**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Expected Accuracy:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NFL team level totals**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Expected Accuracy:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NFL team level spread**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Expected Accuracy:** 
  - **Code Framework:** 
  - **Notes:** 

### NBA Team Level Predictions
- [ ] **Source AND calculations for predictions with code for NBA team level ML**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NBA team level totals**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

### NHL Team Level Predictions
- [ ] **Source AND calculations for predictions with code for NHL team level ML**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NHL team level totals**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NHL team level spread**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

---

## **🏈 PLAYER-LEVEL PREDICTIONS**

- [ ] **Source AND calculations for predictions with code for NFL player level pass yards QB**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NFL player level completions QB**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NFL player level rush yards RB**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NFL player level reception yards WR**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NFL player level receptions WR**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NHL player level shots on goal (SOG)**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NBA player level points**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NBA player level assists**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NBA player level rebounds**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

- [ ] **Source AND calculations for predictions with code for NBA player level 3-pointers made**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Algorithm Approach:** 
  - **Data Inputs Required:** 
  - **Code Framework:** 
  - **Notes:** 

---

## **🗄️ DATABASE & ARCHITECTURE**

- [ ] **What is my database?**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Database Choice:** 
  - **Reasoning:** 
  - **Hosting:** 
  - **Cost:** 
  - **Notes:** 

- [ ] **How to handle all of this in the database. Which database?**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Schema Design:** 
  - **Relationships:** 
  - **Indexing Strategy:** 
  - **Notes:** 

- [ ] **How will I organize all of the predictions best to call upon in the system?**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Data Structure:** 
  - **Query Patterns:** 
  - **Caching Strategy:** 
  - **Notes:** 

---

## **🔧 TECHNOLOGY STACK**

- [ ] **What would be my tech for Discord?**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Language/Framework:** 
  - **Libraries:** 
  - **Hosting:** 
  - **Authentication:** 
  - **Notes:** 

- [ ] **What would be my stack for an app?**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Frontend:** 
  - **Backend:** 
  - **Database:** 
  - **Hosting:** 
  - **Authentication:** 
  - **Notes:** 

---

## **🌤️ WEATHER DATA SOURCES**

- [ ] **Weather API for game location conditions**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API/Source:** 
  - **Data Available:** (Temperature, Wind, Precipitation, Humidity)
  - **Historical Data:** 
  - **Rate Limits:** 
  - **Cost:** 
  - **Example Code:** 
  - **Notes:** 

- [ ] **Integration strategy for weather impact on predictions**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Sports Affected:** (NFL outdoor games, Soccer, etc.)
  - **Impact Factors:** 
  - **Algorithm Integration:** 
  - **Notes:** 

---

## **🤖 AI LLM INTEGRATION (OPENROUTER)**

- [ ] **OpenRouter API setup and configuration**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **API Key Setup:** 
  - **Available Models:** 
  - **Rate Limits:** 
  - **Cost Structure:** 
  - **Example Code:** 
  - **Notes:** 

- [ ] **LLM integration for prediction analysis**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Use Cases:** (Game analysis, trend explanations)
  - **Model Selection:** 
  - **Prompt Engineering:** 
  - **Response Processing:** 
  - **Implementation Framework:** 
  - **Notes:** 

- [ ] **AI-powered user interaction features**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Chat Interface:** 
  - **Query Understanding:** 
  - **Natural Language Responses:** 
  - **Context Management:** 
  - **Notes:** 

- [ ] **LLM for automated insights and reports**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Report Generation:** 
  - **Trend Analysis:** 
  - **Performance Summaries:** 
  - **Scheduling:** 
  - **Notes:** 

---

## **📊 ADVANCED FEATURES**

- [ ] **Is there anything else I can do with the predictions or stats (heavy team based stat organization head to heads)**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Additional Features:** 
  - **Data Requirements:** 
  - **Implementation Complexity:** 
  - **Notes:** 

- [ ] **Possible implement player based stats based on official sources and make player detail cards**
  - **Research Status:** ⏳ Not Started | ✅ Complete
  - **Data Sources:** 
  - **Card Design:** 
  - **Update Frequency:** 
  - **Notes:** 

---

## **📋 COMPLETION TRACKING**

**Total Items:** 54
**Completed:** 0
**In Progress:** 0
**Not Started:** 54

**Completion Percentage:** 0%

---

## **💡 RESEARCH METHODOLOGY**

For each item, follow this process:
1. **Research** - Find 2-3 potential sources/solutions
2. **Compare** - Analyze cost, reliability, features
3. **Test** - Try example code/API calls if possible
4. **Document** - Fill in all fields with findings
5. **Check Off** - Mark as complete only when fully researched

**Remember:** The goal is to have clear answers to ALL of these before writing any production code or subscribing to paid services.

---

_Last Updated: [Date]_
_Next Review: [Date]_