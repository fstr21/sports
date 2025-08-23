# 🎨 Prompting and Customization Guide

Complete guide for customizing Chronulus expert analysis through prompting and configuration.

## Prompting Architecture

### How Chronulus Prompting Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Session Setup  │ -> │  Data Context   │ -> │ Expert Analysis │
│                 │    │                 │    │                 │
│ • situation     │    │ • Pydantic     │    │ • Multiple AI   │
│ • task          │    │   Model Fields  │    │   Experts       │
│ • name          │    │ • Data Values   │    │ • Binary Pred   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1. Session-Level Prompting (Primary Control)

**Location**: `Session()` constructor in MCP server
**Impact**: Highest - defines expert persona and analysis approach

```python
session = Session(
    name="Analysis Session Name",           # Influences AI approach
    situation="Expert persona and context", # Sets expert personality  
    task="Specific analysis instructions",  # Defines output format
    env=dict(CHRONULUS_API_KEY=api_key)
)
```

### 2. Data-Level Context (Secondary Control)

**Location**: Pydantic model field descriptions
**Impact**: Medium - guides data interpretation

```python
class GameData(BaseModel):
    home_team: str = Field(description="Detailed context about home team")
    venue: str = Field(description="Venue advantages and characteristics")
```

## Current Production Configuration

### Expert Persona (Situation)
```python
situation="""You're a seasoned sports bettor with 15+ years of experience 
analyzing MLB games for profit. You've made your living finding edges in the 
market and you talk like it - direct, confident, and cutting through the BS.

You're looking at a classic NL West rivalry matchup between two playoff contenders.
The Dodgers (.570) are slight favorites at -120, while the Padres (.563) are getting 
+102 as home underdogs. Both teams are close in talent but the market sees value 
differences. Petco Park is pitcher-friendly which affects the total.

This could be a spot where the books have it right, or there might be subtle 
value if you dig deeper into the matchup dynamics."""
```

### Analysis Task (Task)
```python
task="""Break down ALL THREE betting markets and tell me where the money is:

1. MONEYLINE: Dodgers -120 vs Padres +102 - which side has value?
2. RUN LINE: Dodgers -1.5 (+146) vs Padres +1.5 (-178) - is the spread right? 
3. TOTAL: Over/Under 8.5 runs - does Petco Park make this an Under spot?

For each market, give me:
- Your pick and confidence level (High/Medium/Low)
- The key factors that drive your decision
- What would make you change your mind
- Your honest assessment of the betting value

Don't write like a textbook. Write like you're breaking down the game with another 
sharp bettor who knows baseball. Use your analysis along with your gut feel.
Give me 12-15 sentences of real insight, not fluff."""
```

## Customization Options

### 🎯 High Customization (Session Level)

#### Different Expert Personas

**1. Sharp Bettor (Current)**
```python
situation="""You're a seasoned sports bettor with 15+ years of experience..."""
```

**2. Statistical Analyst**
```python
situation="""You're a quantitative sports analyst with a PhD in statistics 
and 10 years of experience building predictive models for major sports. You 
approach games through advanced metrics, regression analysis, and statistical 
significance testing. You speak in probabilities and confidence intervals."""
```

**3. Vegas Insider**  
```python
situation="""You're a former Las Vegas sportsbook manager who set lines for 
10 years at major casinos. You understand how the house thinks, where they're 
vulnerable, and how public perception affects line movement. You know which 
numbers are sharp and which are traps."""
```

**4. Baseball Scout**
```python
situation="""You're a former MLB scout with 20 years of experience evaluating 
talent and predicting performance. You focus on matchups, player tendencies, 
situational factors, and intangibles that don't show up in box scores."""
```

#### Different Analysis Formats

**1. Structured Report**
```python
task="""Provide a structured analysis report:

## Executive Summary (2 sentences)
## Statistical Analysis  
- Key metrics and trends
- Performance indicators
## Market Efficiency Assessment
- Line accuracy evaluation  
- Public vs sharp money
## Risk/Reward Analysis
- Probability assessments
- Expected value calculations
## Final Recommendations
- Confidence scores (1-10)
- Recommended bet sizes"""
```

**2. Contrarian Focus**
```python
task="""Find the contrarian plays - where is the public wrong?

Focus on:
- Public betting percentages vs line movement
- Narrative-driven overreactions  
- Recency bias in the market
- Situations where conventional wisdom fails

Give me the anti-public plays with reasoning."""
```

**3. Quick Picks Format**
```python
task="""Give me rapid-fire picks in this format:

PICK 1: [Team] [Line] - [Confidence: H/M/L] - [2 sentence reason]
PICK 2: [Market] [Side] - [Confidence: H/M/L] - [2 sentence reason]  
PICK 3: [Market] [Side] - [Confidence: H/M/L] - [2 sentence reason]

Keep it tight, keep it sharp. No fluff."""
```

#### Dynamic Context Integration

**Game-Specific Situations**
```python
def build_situation(game_data):
    base_situation = "You're a seasoned sports bettor..."
    
    # Add context based on game data
    if game_data.home_win_pct > 0.600:
        base_situation += f"\nThe {game_data.home_team} are having a dominant season at {game_data.home_win_pct:.1%}..."
    
    if "rivalry" in game_data.context:
        base_situation += "\nThis is a heated rivalry where records often go out the window..."
    
    if game_data.playoff_implications:
        base_situation += "\nThere are significant playoff implications riding on this game..."
    
    return base_situation
```

### ⚖️ Medium Customization (Data Models)

#### Rich Field Descriptions
```python
class EnhancedGameData(BaseModel):
    home_team: str = Field(
        description="Home team with recent form, key injuries, and motivational factors"
    )
    venue: str = Field(
        description="Detailed venue analysis including weather, dimensions, and historical scoring patterns"
    )
    betting_context: str = Field(
        description="Market movement, public betting percentages, and sharp money indicators"
    )
```

#### Contextual Data Values
```python
game_data = EnhancedGameData(
    home_team="San Diego Padres (hot 7-3 streak, getting healthy, playing for playoff spot)",
    venue="Petco Park (pitcher-friendly, 8.3 avg runs, marine layer affects fly balls)",
    betting_context="Line moved from +105 to +102, 67% public money on Dodgers"
)
```

### 🔒 Limited Customization (Fixed Parameters)

#### Expert Count
```python
num_experts=2        # Minimum (cost: ~$0.05-0.10)
num_experts=5        # Balanced (cost: ~$0.15-0.25)  
num_experts=10       # Comprehensive (cost: ~$0.30-0.50)
num_experts=30       # Maximum (cost: ~$1.50-3.00)
```

#### Analysis Depth
```python
note_length=(5, 8)   # Brief analysis
note_length=(10, 15) # Standard depth (current)
note_length=(15, 20) # Very detailed
```

## Implementation Examples

### Custom Expert Profiles

**1. Adding New Expert Type**
```python
def create_quant_session(game_data):
    return Session(
        name="Quantitative MLB Analysis",
        
        situation="""You're a quantitative analyst who built predictive models 
        for DraftKings. You think in terms of expected value, Bayesian inference, 
        and Monte Carlo simulations. You trust numbers over narratives.""",
        
        task="""Run the numbers and give me:
        1. Expected value calculations for each bet
        2. Confidence intervals for your predictions  
        3. Kelly Criterion bet sizing recommendations
        4. Statistical significance of key factors
        
        Show your work with specific metrics and probabilities."""
    )
```

**2. Multi-Mode Analysis**
```python
async def multi_perspective_analysis(game_data):
    # Run multiple expert types
    sharp_analysis = await get_analysis(game_data, expert_type="sharp_bettor")
    quant_analysis = await get_analysis(game_data, expert_type="quantitative") 
    scout_analysis = await get_analysis(game_data, expert_type="scout")
    
    return {
        "consensus": combine_analyses([sharp_analysis, quant_analysis, scout_analysis]),
        "individual_perspectives": {
            "sharp_bettor": sharp_analysis,
            "quantitative": quant_analysis, 
            "scout": scout_analysis
        }
    }
```

### Dynamic Prompting

**Context-Aware Sessions**
```python
def build_dynamic_session(game_data):
    # Base expert persona
    situation = "You're an experienced sports bettor..."
    
    # Add relevant context
    if game_data.is_playoff_race:
        situation += "\nThis game has major playoff implications..."
    
    if game_data.weather_concerns:
        situation += f"\nWeather could be a factor: {game_data.weather}..."
    
    if game_data.key_injuries:
        situation += f"\nInjury concerns: {game_data.key_injuries}..."
    
    # Dynamic task based on market conditions
    if game_data.line_movement > 2:
        task_focus = "Focus on why this line has moved significantly..."
    elif game_data.public_percentage > 80:
        task_focus = "Look for contrarian value against heavy public betting..."
    else:
        task_focus = "Standard market analysis..."
    
    return Session(name="Dynamic Analysis", situation=situation, task=task_focus)
```

## Testing Different Prompts

### A/B Testing Framework
```python
async def test_prompt_variations(game_data):
    variations = [
        {"type": "sharp_bettor", "persona": sharp_bettor_prompt},
        {"type": "quantitative", "persona": quant_analyst_prompt},
        {"type": "contrarian", "persona": contrarian_prompt}
    ]
    
    results = {}
    for variation in variations:
        analysis = await get_chronulus_analysis(
            game_data=game_data,
            expert_persona=variation["persona"]
        )
        results[variation["type"]] = analysis
    
    return compare_predictions(results)
```

## Best Practices

### Prompt Engineering Guidelines

1. **Be Specific**: Clear instructions produce better results
2. **Set Context**: Rich situational context improves analysis quality  
3. **Define Format**: Specify exactly what output you want
4. **Use Domain Language**: Sports betting terminology works best
5. **Test Variations**: A/B test different prompts for optimal results

### Performance Optimization

1. **Fewer Experts**: Use 2-3 experts for speed and cost efficiency
2. **Shorter Analysis**: 8-12 sentences for faster responses
3. **Focused Tasks**: Narrow scope produces more actionable insights
4. **Cache Sessions**: Reuse session objects when possible

### Cost Management

1. **Expert Count**: Linear cost scaling (2 experts = ~$0.05-0.10)
2. **Analysis Length**: Minimal impact on cost
3. **Session Reuse**: No additional cost for multiple requests
4. **Batch Requests**: Group similar analyses together

This comprehensive customization framework allows you to tailor Chronulus analysis to any specific use case, expert perspective, or output format needed for your sports betting analysis workflows.