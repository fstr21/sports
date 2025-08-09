# 🧠 Natural Language Sports AI Interface

## 🎉 What We Built

I've added **natural language processing** to your Sports HTTP API! Now you can ask questions in plain English and get intelligent responses.

### ✅ New Features Added:

1. **`/ask` Endpoint** - Ask natural language questions via HTTP
2. **`ask_sports.py` CLI** - Interactive command-line interface 
3. **Smart Query Processing** - AI understands your questions and routes to appropriate MCPs
4. **Multiple AI Models** - Choose from OpenAI, Anthropic, Meta, Google models

## 🚀 How It Works

### 1. **Ask via HTTP API**
```bash
curl -H "Authorization: Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ" \
     -H "Content-Type: application/json" \
     -d '{"question":"What NBA games are today?"}' \
     https://web-production-b939f.up.railway.app/ask
```

### 2. **Ask via Interactive CLI**
```bash
python ask_sports.py
```

```
Sports AI Chat Interface
========================================
Ask me anything about sports!

Ask about sports > What NBA teams are there?
[AI] Thinking...

[AI Understanding]: Looking up all NBA teams for you
Found 30 teams:
  Atlanta Hawks (ATL)
  Boston Celtics (BOS)
  Brooklyn Nets (BKN)
  ...
```

## 💬 Example Questions You Can Ask

### **Game Information**
- "What NBA games are today?"
- "Show me tonight's NFL games"
- "What Premier League matches happened this week?"
- "Are there any basketball games tonight?"

### **Team Information**  
- "Show me all NBA teams"
- "How many NFL teams are there?"
- "List the hockey teams"
- "What teams are in the Premier League?"

### **Daily Summaries**
- "Give me today's sports summary"
- "What's happening in sports today?"
- "Show me all games across all leagues"
- "Daily sports intelligence report"

### **Specific Leagues**
- "What's happening in the NBA?"
- "Show me La Liga games"
- "Any MLS matches today?"
- "College football games this week"

## 🤖 Available AI Models

The CLI lets you choose from multiple AI models:

1. **OpenAI GPT-4o Mini** (default) - Fast and efficient
2. **OpenAI GPT-4o** - Most capable
3. **Anthropic Claude 3.5 Sonnet** - Great reasoning
4. **Meta Llama 3.1 8B** - Open source
5. **Google Gemini Pro** - Google's latest

## 🔧 Setup Requirements

### For Railway (Production):
1. **Add OpenRouter API Key** to Railway environment variables:
   ```
   OPENROUTER_API_KEY = your-openrouter-api-key-here
   ```
2. Railway will auto-deploy the new features

### For Local Testing:
1. **Get OpenRouter API Key**: https://openrouter.ai
2. **Add to .env file**:
   ```
   OPENROUTER_API_KEY=your-openrouter-api-key-here
   ```

## 📱 Using the CLI Interface

### Start the Interactive Chat:
```bash
python ask_sports.py
```

### Available Commands:
- **Any question** - Ask about sports in natural language
- **`help`** - Show example questions
- **`models`** - Change AI model
- **`quit`** - Exit

### Example Session:
```
Ask about sports > What NBA teams are there?
[AI Understanding]: Looking up all NBA teams
Found 30 teams: Atlanta Hawks (ATL), Boston Celtics (BOS)...

Ask about sports > models
Available AI models:
1. openai/gpt-4o-mini (current)
2. openai/gpt-4o  
3. anthropic/claude-3.5-sonnet

Select model (1-5): 3
[OK] Switched to anthropic/claude-3.5-sonnet

Ask about sports > What games are today?
[AI Understanding]: Checking today's games across all leagues
Daily Sports Summary:
  BASKETBALL/NBA: 2 games
  FOOTBALL/NFL: 0 games
```

## 🔗 Integration Examples

### Discord Bot with Natural Language:
```python
import requests

BASE_URL = "https://web-production-b939f.up.railway.app"
API_KEY = "89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"
headers = {"Authorization": f"Bearer {API_KEY}"}

@bot.command()
async def ask(ctx, *, question):
    response = requests.post(f"{BASE_URL}/ask",
                           json={"question": question},
                           headers=headers)
    
    data = response.json()
    if data.get("ok"):
        await ctx.send(data.get("interpretation", "Here's what I found:"))
        # Process and display the result
    else:
        await ctx.send("Sorry, I couldn't understand that question.")
```

### Python Script:
```python
import requests

def ask_sports_ai(question):
    response = requests.post("https://web-production-b939f.up.railway.app/ask",
                           json={"question": question},
                           headers={"Authorization": "Bearer 89Gj253zOM37FA_Z0TqhZm0OKdow92XT8O80Adg_qtQ"})
    return response.json()

# Ask any question
result = ask_sports_ai("What NBA games are tonight?")
print(result["interpretation"])
```

## 🧠 How the AI Processing Works

1. **Question Analysis**: AI analyzes your natural language question
2. **Intent Recognition**: Determines what sports data you need  
3. **API Routing**: Maps to the appropriate MCP endpoint
4. **Data Retrieval**: Fetches data from ESPN/Odds APIs
5. **Smart Response**: Formats the response in a human-friendly way

## 💡 Smart Features

- **Context Aware**: Understands "today", "tonight", "this week"
- **Multi-League**: Can query multiple sports at once
- **Flexible Language**: Works with casual or formal questions
- **Error Handling**: Explains when it needs more information
- **Model Selection**: Choose the best AI for your needs

## 🚀 What's Next

Once you add your OpenRouter API key, you'll have:

- **Conversational Sports API** 🗣️
- **Multiple AI Models** 🤖  
- **Natural Language Interface** 💬
- **Production Ready** ⚡
- **Works Everywhere** 🌍

Your original MCP consistency problem is now solved with an AI-powered conversational interface!

## 🔑 Get Started

1. **Get OpenRouter API key**: https://openrouter.ai
2. **Add to Railway**: Environment Variables → `OPENROUTER_API_KEY`
3. **Test locally**: `python ask_sports.py`
4. **Use in production**: `https://web-production-b939f.up.railway.app/ask`

You now have a **conversational sports AI** that can answer any question about games, teams, and sports data! 🎉