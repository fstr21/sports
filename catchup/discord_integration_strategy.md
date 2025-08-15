# Discord Integration Strategy for Sports Betting Platform

## Overview
This document outlines the approach for integrating both a **Discord Bot** and a **Discord MCP** into the sports betting analytics platform. It explains their roles, how they work together, and why the morning betting recommendations should be handled by the bot calling an LLM, while the Discord MCP is used for ad-hoc AI-driven interactions.

---

## Goals
- Deliver **daily morning betting recommendations** for all games, with odds, stats, predictions, and an AI-generated reasoning ("why we chose this bet").
- Support **ad-hoc, natural language queries** from users during the day, without triggering unnecessary API calls.
- Minimize API usage while maximizing automation and interactivity.

---

## Recommended Division of Responsibilities

### Morning Procedure (Bot-Led)
**Responsible Component:** Discord Bot

**Reasoning for Bot Ownership:**
1. **Predictable, structured task:** Morning updates are repeatable and time-based.
2. **API efficiency:** Bot already has all required data from Quad MCPs, no need for MCP to re-fetch.
3. **Formatting control:** Bot can merge odds, stats, predictions, and LLM reasoning into a single message.

**Flow:**
1. **Fetch Data:** Bot retrieves games, odds, and stats from Quad MCPs (MLB, Soccer, CFB, Odds MCP).
2. **Run Predictions:** Apply prediction logic.
3. **Call LLM API:** Provide relevant data and ask for a concise reasoning.
4. **Format Output:** Merge into a complete message.
5. **Post to Discord:** Send directly to the appropriate league/game channel.

**Example Message Format:**
```
🏟 Game: Yankees @ Red Sox
💰 Odds: Yankees -130, Red Sox +115
📊 Stats: Yankees 7-3 last 10, Red Sox 5-5
🎯 Prediction: Yankees ML
📝 Reason: Based on strong bullpen performance and recent win streak.
```

---

### Ad-Hoc Queries & AI Interactions (MCP-Led)
**Responsible Component:** Discord MCP + LLM

**When Used:**
- User asks a question later in the day (e.g., "Any underdog bets worth taking tonight?").
- AI posts updates about significant game changes (injuries, weather, odds swings).

**Advantages:**
- No need to modify bot code for every new interaction.
- AI can read previously posted data from Discord without hitting sports data APIs.
- Supports two-way interaction between subscribers and the AI.

**Flow:**
1. **User Query:** Appears in Discord channel.
2. **Read Messages:** AI uses Discord MCP's `read_messages` tool to get morning posts.
3. **Analyze:** AI processes info and formulates answer.
4. **Respond:** AI uses `send_message` tool to post reply.

---

## Why Morning LLM Reasoning Should Be Bot-Led
- **Efficiency:** Data is already in bot memory; no double API calls.
- **Consistency:** Ensures every morning post has a uniform style and includes reasoning.
- **Simplicity:** Keeps morning job in one place, avoiding orchestration complexity.

---

## Suggested Architecture
```
[Quad MCPs] ---> [Discord Bot: Fetch + Predict + LLM Reasoning] ---> [Morning Discord Posts]
                                                    |
                                                    V
                                       [Discord Channels with Stored Data]
                                                    |
                                                    V
                                    [Discord MCP + LLM: Read + Respond to Queries]
```

---

## Summary Table

| Task                                  | Bot | Discord MCP |
|---------------------------------------|-----|-------------|
| Fetch morning game data               | ✅  | ❌          |
| Run daily predictions                 | ✅  | ❌          |
| Call LLM for morning reasoning        | ✅  | ❌          |
| Post structured morning updates       | ✅  | ❌          |
| Read morning posts for later analysis | ❌  | ✅          |
| Respond to user betting questions     | ❌  | ✅          |
| Post ad-hoc AI updates                 | ❌  | ✅          |

---

## Final Recommendation
- **Morning updates:** Bot handles data fetching, predictions, LLM reasoning, and posting.
- **Daytime queries & ad-hoc posts:** Discord MCP allows AI to interact directly with Discord without triggering fresh API calls.
- This hybrid approach ensures efficiency, keeps API usage predictable, and maximizes interactivity for your subscribers.
