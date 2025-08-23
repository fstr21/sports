# 🚀 Setup Instructions - Custom Chronulus Testing

## ✅ COMPLETED SETUP

Everything is ready to test! Here's what was created:

### 📁 Directory Structure
```
testing_custom_chron/
├── custom_chronulus_openrouter.py     # Main OpenRouter implementation
├── reverse_engineer_chronulus.py      # Original OpenAI version
├── CHRONULUS_REVERSE_ENGINEERING_README.md  # Technical documentation
├── requirements.txt                    # Dependencies
├── README.md                          # User guide
├── test_runner.py                     # Quick test script
└── SETUP_INSTRUCTIONS.md             # This file
```

### 🔧 Configuration Status
- ✅ **OpenRouter API Key**: Configured in .env.local
- ✅ **Model**: `openai/gpt-oss-20b:free` (cost-effective!)
- ✅ **Game Data**: Real Red Sox @ Yankees data from image hard-coded
- ✅ **Expert Count**: Set to 2 agents for testing
- ✅ **Dependencies**: All required packages listed in requirements.txt

### 🎯 Real Test Data Loaded
From your image copy 2.png:
- **Game**: Boston Red Sox @ New York Yankees
- **Moneyline**: Red Sox -132 (favorites), Yankees +112 (underdogs)  
- **Records**: Red Sox 70-59 (.543), Yankees 69-59 (.539)
- **Recent Form**: Red Sox 5-5 L10, Yankees 7-3 L10 (Yankees hot!)
- **Context**: AL East rivalry with playoff implications

## 🚀 HOW TO RUN

### Option 1: Quick Test
```bash
cd testing_custom_chron
python test_runner.py
```

### Option 2: Full Test
```bash
cd testing_custom_chron  
python custom_chronulus_openrouter.py
```

### Option 3: Install Dependencies First (if needed)
```bash
cd testing_custom_chron
pip install -r requirements.txt
python custom_chronulus_openrouter.py
```

## 🎯 Expected Output

You should see:
1. **Environment Check**: OpenRouter API key and model verification
2. **Game Analysis**: 2 expert panel analyzing Red Sox @ Yankees  
3. **Expert Opinions**: Statistical and Situational expert perspectives
4. **Consensus Result**: Combined probability with Beta distribution
5. **Betting Analysis**: Edge calculation vs market odds
6. **Cost Report**: Actual OpenRouter usage cost

## 💰 Cost Expectations

Using `openai/gpt-oss-20b:free`:
- **Expected Cost**: $0.00 (free tier!)
- **vs Chronulus**: 100% savings
- **Quality**: Should be decent for testing purposes

## 📊 What to Look For

### Good Signs:
- ✅ Both experts provide different probability estimates
- ✅ Analysis mentions rivalry factors, recent form, etc.
- ✅ Consensus probability seems reasonable (40-60% range)
- ✅ Betting edge calculation vs -132 moneyline

### Red Flags:
- ❌ Both experts give identical probabilities (50/50)
- ❌ Analysis is generic or doesn't mention game specifics
- ❌ API errors or timeouts
- ❌ Consensus probability is extreme (>80% or <20%)

## 🔧 Troubleshooting

### "OPENROUTER_API_KEY not found"
- Check that .env.local is in the parent directory
- Make sure the API key is valid

### "Model not found" or API errors  
- Try changing OPENROUTER_MODEL in .env.local to:
  - `anthropic/claude-3.5-sonnet` (higher quality, costs money)
  - `openai/gpt-4o-mini` (good balance)
  - `meta-llama/llama-3.1-8b-instruct:free` (free alternative)

### Slow performance
- Free models can be slower
- Consider upgrading to paid models for faster response

## 🎉 SUCCESS CRITERIA

The test is successful if:
1. ✅ Script runs without errors
2. ✅ 2 different expert analyses are generated
3. ✅ Final probability is between 30-70% 
4. ✅ Betting edge calculation makes sense
5. ✅ Analysis mentions Red Sox/Yankees specifics
6. ✅ Results saved to JSON file

## 🚀 Next Steps After Testing

1. **Compare Quality**: How does this compare to real Chronulus?
2. **Model Testing**: Try different OpenRouter models
3. **Railway Deployment**: Convert to MCP server format
4. **Discord Integration**: Replace Chronulus calls in your bot
5. **Cost Analysis**: Track actual usage costs

## 📞 Quick Commands Summary

```bash
# Navigate to directory
cd testing_custom_chron

# Quick test
python test_runner.py

# Full analysis  
python custom_chronulus_openrouter.py

# Check what was created
ls -la
```

Everything is ready to go! 🚀