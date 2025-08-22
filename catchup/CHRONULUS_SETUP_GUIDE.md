# 🧠 Chronulus AI Forecasting - Complete Setup Guide
*For Sports Betting Analysis Integration*

## 📋 Overview

This guide provides complete setup instructions for integrating **Chronulus AI Expert Panel Forecasting** into your sports analysis platform. Chronulus provides institutional-quality sports betting analysis using multiple AI experts to assess game probabilities and market value.

---

## 🎯 What is Chronulus?

### Core Concept
Chronulus is an **AI expert panel service** that analyzes sports data using 2-30 independent AI experts to provide:
- **Probability Assessments**: Win/loss predictions for binary outcomes
- **Detailed Reasoning**: 5-15 sentence explanations from each expert
- **Consensus Analysis**: Averaged expert opinions with confidence intervals
- **Market Value Analysis**: Edge detection vs betting odds

### Key Benefits for Sports Betting
- **Sophisticated Analysis**: Institutional-quality expert reasoning
- **Market Inefficiency Detection**: Identifies when books might be wrong
- **Educational Content**: Teaches users about betting factors
- **Cost Effective**: ~$0.05-0.10 per prediction
- **Professional Quality**: Much deeper than basic prediction models

---

## 🏗️ Technical Architecture

### How Chronulus Works
```
Your Game Data → Chronulus API → Expert Panel (2-30 AI analysts)
      ↓                ↓                    ↓
Structured Input → JSON-RPC 2.0 → Independent Analysis
      ↓                ↓                    ↓
Team Stats      → Session Context → Detailed Reasoning
Recent Form     → Task Definition → Probability Assessment
Betting Lines   → Expert Count    → Consensus + Confidence
      ↓                ↓                    ↓
Final Output ← Betting Recommendation ← Expert Consensus
```

### Core Components
1. **Session**: Defines situation and task context
2. **BinaryPredictor**: Agent that handles win/loss predictions  
3. **Expert Panel**: 2-30 AI experts analyze independently
4. **Consensus**: Averaged probabilities with confidence ranges
5. **Market Analysis**: Edge calculation vs current betting odds

---

## 🚀 Setup Instructions

### Step 1: Account Creation and API Access

1. **Sign up for Chronulus**:
   - Visit: https://chronulus.ai
   - Create account with email verification
   - Choose pricing tier (start with basic tier for testing)

2. **Get API Key**:
   - Navigate to API settings in dashboard
   - Generate new API key
   - Copy the key (format: `chronulus_xxxxxxxxx`)

3. **Check Pricing**:
   - **Basic Tier**: ~$5-10/month for testing (50-100 predictions)
   - **Professional**: ~$50-100/month for production usage
   - **Cost per prediction**: ~$0.05-0.10 depending on expert count

### Step 2: Local Development Environment

1. **Install Chronulus SDK**:
   ```bash
   pip install chronulus
   ```

2. **Environment Configuration**:
   Create `.env.local` in your project root:
   ```bash
   CHRONULUS_API_KEY=your_api_key_here
   ```

3. **Test Connection**:
   ```python
   from chronulus import Session
   
   session = Session(
       name="Test Connection",
       situation="Testing Chronulus API connectivity",
       task="Verify API access and basic functionality",
       env=dict(CHRONULUS_API_KEY="your_key_here")
   )
   
   session.create()
   print(f"Connected! Session ID: {session.session_id}")
   ```

### Step 3: Testing Framework Setup

1. **Clone Testing Scripts**:
   ```bash
   # Copy the comprehensive testing framework
   mkdir chronulus_testing
   cd chronulus_testing
   ```

2. **Download Core Scripts**:
   - `comprehensive_2_expert_analysis.py` - Main analysis script
   - `humanize_analysis.py` - Makes output more conversational
   - `check_results.py` - Manual result checking

3. **Directory Structure**:
   ```
   chronulus_testing/
   ├── comprehensive_2_expert_analysis.py    # Main analysis script
   ├── humanize_analysis.py                  # Post-processing for natural language
   ├── check_results.py                      # Manual result checking
   ├── results/                              # Generated analysis reports
   │   ├── comprehensive_analysis_TIMESTAMP.md
   │   ├── comprehensive_analysis_TIMESTAMP.json
   │   └── comprehensive_analysis_TIMESTAMP_humanized.md
   └── .env.local                            # Your API key
   ```

### Step 4: Run Your First Analysis

1. **Basic Test**:
   ```bash
   python comprehensive_2_expert_analysis.py
   ```

2. **Expected Output**:
   - 2 AI experts analyze the game data
   - 10-15 sentence detailed explanations each
   - Consensus probability assessment
   - Market value analysis (edge calculation)
   - Betting recommendation (BET/NO BET)

3. **Review Results**:
   - Check `/results` folder for generated files
   - Review Markdown report for detailed analysis
   - Check JSON file for structured data

---

## 🎯 Integration with Discord Bot

### Phase 1: Testing Integration (Recommended First Step)

1. **Add to MLBHandler**:
   ```python
   # In mlb_handler.py, add new embed generation
   async def create_chronulus_analysis_embed(self, game_data):
       # Call Chronulus API with game data
       # Generate 6th embed with AI forecasting
       pass
   ```

2. **Expert Analysis Embed Structure**:
   ```python
   embed = discord.Embed(
       title="🧠 AI Expert Forecast & Value Analysis",
       description=f"2-Expert Consensus Analysis",
       color=0x9932CC  # Purple for AI analysis
   )
   
   embed.add_field(
       name="Expert Consensus", 
       value=f"{consensus_probability:.1%} win probability",
       inline=True
   )
   
   embed.add_field(
       name="Market Value",
       value=f"Edge: {edge:+.1%} | {recommendation}",
       inline=True
   )
   
   embed.add_field(
       name="Key Expert Insights",
       value=f"Expert 1: {expert1_summary}\nExpert 2: {expert2_summary}",
       inline=False
   )
   ```

### Phase 2: Production Integration

1. **Environment Variables**:
   ```bash
   # Add to Discord bot environment
   CHRONULUS_API_KEY=your_api_key_here
   ENABLE_CHRONULUS_ANALYSIS=true
   CHRONULUS_EXPERT_COUNT=2
   ```

2. **Error Handling**:
   ```python
   try:
       chronulus_analysis = await get_chronulus_analysis(game_data)
       embeds.append(create_chronulus_embed(chronulus_analysis))
   except Exception as e:
       logger.warning(f"Chronulus analysis failed: {e}")
       # Continue with other embeds, don't fail entire analysis
   ```

3. **Rate Limiting**:
   - Limit to 2 experts per game for cost control
   - Consider caching results for repeated queries
   - Monitor API usage via Chronulus dashboard

---

## 📊 Expected Results and Quality

### Sample Expert Analysis Output

**Game**: Colorado Rockies @ Pittsburgh Pirates (+160 vs -190)

**Expert 1 Analysis** (2-expert consensus: 35.7% Rockies win):
*"Look, the Rockies are garbage this year (37-91) but they're absolutely scorching hot right now (7-3 L10). This screams potential value bet if the recent form is real and the market is still stuck on season-long stats. The Pirates can't buy a win lately (3-7 L10) despite being the better team on paper. PNC Park helps Pittsburgh some, but when you're this cold, home field doesn't matter much. I'm thinking the books are slow to adjust to this momentum flip..."*

**Market Analysis**:
- **Chronulus Consensus**: 35.7% Rockies win
- **Market Implied**: 38.5% at +160 odds
- **Edge**: -2.7% (No betting value)
- **Recommendation**: NO BET - Market appears efficient

### Quality Indicators
- **Detailed Reasoning**: 10-15 sentences per expert explaining their logic
- **Factor Analysis**: Recent form vs season stats, home field, motivation, etc.
- **Market Awareness**: Understanding of betting lines and value concepts
- **Conversational Tone**: Natural language, not academic/robotic
- **Actionable Insights**: Clear betting recommendations with reasoning

---

## 💰 Cost Management

### API Usage Optimization

1. **2-Expert Minimum**: Balance quality vs cost (~8-10 API calls per game)
2. **Selective Usage**: Only analyze games with interesting betting situations
3. **Batch Processing**: Analyze multiple games in sequence if needed
4. **Usage Monitoring**: Track API calls via Chronulus dashboard

### Cost Examples
- **Single Game Analysis**: $0.05-0.10 (2 experts)
- **Daily MLB Slate**: $1.50-3.00 (15 games × 2 experts)
- **Monthly Usage**: $25-50 for regular analysis
- **ROI Calculation**: Prevents one bad $25 bet per month = profitable

---

## 🔧 Troubleshooting

### Common Issues

1. **API Key Problems**:
   ```python
   # Test API key validity
   from chronulus import Session
   try:
       session = Session(name="Test", situation="Test", task="Test", 
                        env=dict(CHRONULUS_API_KEY="your_key"))
       session.create()
       print("API key valid!")
   except Exception as e:
       print(f"API key issue: {e}")
   ```

2. **Timeout Issues**:
   ```python
   # Extend timeout for detailed analysis
   predictions = predictor.get_request_predictions(
       request_id=request.request_id,
       try_every=15,  # Check every 15 seconds
       max_tries=20   # Wait up to 5 minutes
   )
   ```

3. **Response Parsing**:
   ```python
   # Probability extraction from tuples
   if hasattr(pred, 'prob') and isinstance(pred.prob, tuple):
       probability = pred.prob[0]  # First element = win probability
   ```

### Debug Tools
- **Request ID Tracking**: Save request IDs for manual result checking
- **Response Structure Analysis**: Use debug scripts to understand API responses
- **Error Logging**: Comprehensive logging for troubleshooting

---

## 📈 Performance Benchmarks

### Response Times
- **2-Expert Analysis**: 30-90 seconds
- **5-Expert Analysis**: 90-180 seconds
- **API Call Overhead**: ~200ms per call
- **Total Integration Time**: <2 minutes for 2-expert analysis

### Quality Metrics
- **Expert Agreement**: High agreement (>95%) indicates strong consensus
- **Market Efficiency Detection**: Successfully identifies when markets are efficient
- **Educational Value**: Rich explanations teach betting concepts
- **Professional Quality**: Institutional-level analysis depth

---

## 🎯 Next Steps

### Immediate Actions
1. **Sign up for Chronulus account** and get API key
2. **Run test analysis** using provided scripts
3. **Review output quality** in generated Markdown/JSON files
4. **Evaluate integration potential** for your Discord bot

### Integration Planning
1. **Phase 1**: Add as optional 6th embed for testing
2. **Phase 2**: Refine based on user feedback
3. **Phase 3**: Expand to other sports if successful
4. **Phase 4**: Advanced features (historical analysis, trend detection)

### Success Metrics
- **User Engagement**: Do users find AI analysis valuable?
- **Betting Performance**: Does it help users make better decisions?
- **Cost Effectiveness**: ROI vs monthly subscription cost
- **Educational Impact**: Are users learning from expert reasoning?

---

## 📞 Support Resources

### Chronulus Documentation
- **SDK Documentation**: https://docs.chronulus.ai
- **API Reference**: Complete tool and parameter documentation
- **Example Implementations**: Multiple use cases and code samples

### Testing Framework
- **Location**: `C:\Users\fstr2\Desktop\sports\testing\chronulus_forecasting\`
- **Main Script**: `comprehensive_2_expert_analysis.py`
- **Humanizer**: `humanize_analysis.py` for natural language output
- **Manual Checker**: `check_results.py` for debugging

### Integration Support
- **Discord Bot Integration**: Add to existing MLBHandler as 6th embed
- **Error Handling**: Graceful degradation if Chronulus unavailable
- **Cost Control**: 2-expert limit with usage monitoring

---

*This setup guide provides everything needed to integrate Chronulus AI expert forecasting into your sports analysis platform. The testing framework is ready to use and the integration path is clearly defined.*