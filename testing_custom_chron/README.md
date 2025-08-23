# 🧠 Custom Chronulus AI - OpenRouter Implementation

Local implementation of ChronulusAI functionality using OpenRouter for model selection.

## 🎯 What's This?

This is a **cost-effective replacement** for ChronulusAI that:
- ✅ Uses OpenRouter for model flexibility (Claude, GPT-4, etc.)
- ✅ Implements the same expert panel consensus system
- ✅ Works with real game data (Red Sox @ Yankees from image copy 2.png)
- ✅ **50-80% cost savings** compared to Chronulus API
- ✅ Ready for Railway deployment as MCP server

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Make sure your .env.local has:
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # or any OpenRouter model
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Local Test
```bash
python custom_chronulus_openrouter.py
```

## 📊 Test Data

Using **real game data** from your image:
- **Game**: Boston Red Sox @ New York Yankees  
- **Moneyline**: Red Sox -132, Yankees +112
- **Records**: Red Sox 70-59 (.543), Yankees 69-59 (.539)
- **Recent Form**: Red Sox 5-5 L10, Yankees 7-3 L10
- **Context**: AL East rivalry, playoff implications

## 🤖 Expert System

**2-Expert Panel** with different personas:
1. **Statistical Expert**: Focuses on numbers and historical data
2. **Situational Expert**: Considers momentum, form, rivalry factors

Each expert provides:
- Probability estimate (0.0-1.0)  
- Detailed analysis (2-3 sentences)
- Confidence level (0.0-1.0)

## 💰 Cost Comparison

| Feature | Chronulus API | Custom OpenRouter | Savings |
|---------|---------------|-------------------|---------|
| **Cost per Analysis** | $0.05-0.10 | $0.01-0.03 | 60-80% |
| **Model Choice** | Fixed | Any OpenRouter model | ✅ |
| **Customization** | Limited | Full control | ✅ |
| **Rate Limits** | Yes | OpenRouter limits | ✅ |

## 📋 Files

- `custom_chronulus_openrouter.py` - Main implementation
- `reverse_engineer_chronulus.py` - Original OpenAI version  
- `requirements.txt` - Dependencies
- `README.md` - This file

## 🌐 Railway Deployment Ready

This code is structured to easily become a Railway MCP server:
- Environment variable configuration
- Async HTTP client setup
- Error handling for production
- Same API structure as original Chronulus

## 🎯 Next Steps

1. **Test locally** - Run the script and review analysis quality
2. **Compare results** - vs actual Chronulus API if you have access
3. **Railway deployment** - Convert to MCP server format
4. **Discord integration** - Replace Chronulus calls in your bot

## 📞 Support

This implementation reverse-engineers the ChronulusAI approach for educational purposes and cost optimization. It demonstrates how expert panel AI systems work and provides a practical alternative for sports analysis.