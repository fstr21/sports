# CFB Rankings Tool - README

## Overview
The `rankings.py` tool tests the **getCFBRankings** MCP endpoint, which retrieves college football rankings and polls from the deployed CFB MCP server. This tool validates ranking data across multiple polls and time periods.

## MCP Tool: getCFBRankings

### Description
Retrieves college football rankings from various polls including AP Top 25, Coaches Poll, CFP Rankings, and other major polling systems from the College Football Data API.

### Parameters
- **year** (integer, optional): Season year (default: current year)
- **week** (integer, optional): Week number (1-15 for regular season)
- **season_type** (string, optional): Season type ("regular", "postseason")

### Example Usage

#### Get Current Week Rankings
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBRankings",
    "arguments": {
      "year": 2024,
      "week": 15
    }
  }
}
```

#### Get Preseason Rankings
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBRankings",
    "arguments": {
      "year": 2024,
      "week": 1
    }
  }
}
```

#### Get Postseason Rankings
```json
{
  "method": "tools/call",
  "params": {
    "name": "getCFBRankings",
    "arguments": {
      "year": 2024,
      "season_type": "postseason"
    }
  }
}
```

## Test Cases

### 1. 2024 Final Rankings
- **Purpose**: Test end-of-season rankings across all polls
- **Expected**: Complete final rankings with playoff implications
- **Polls**: AP, Coaches, CFP, and other major polls
- **Analysis**: Season-ending team evaluations

### 2. 2024 Week 1 Rankings
- **Purpose**: Test preseason/early season rankings
- **Expected**: Preseason expectations and early season adjustments
- **Polls**: Preseason AP and Coaches polls
- **Analysis**: Preseason vs final ranking comparisons

### 3. 2024 Postseason Rankings
- **Purpose**: Test playoff and bowl game rankings
- **Expected**: CFP rankings and bowl selection criteria
- **Polls**: College Football Playoff Committee rankings
- **Analysis**: Playoff selection and seeding

## Major Polling Systems

### Primary Polls
- **AP Top 25**: Associated Press poll (media voters)
- **Coaches Poll**: USA Today Coaches poll (coaches voters)
- **CFP Rankings**: College Football Playoff Committee rankings

### Secondary Polls
- **FCS Coaches Poll**: FCS division rankings
- **AFCA Division II**: Division II coaches poll
- **AFCA Division III**: Division III coaches poll

### Historical Polls
- **BCS Rankings**: Historical BCS era rankings (1998-2013)
- **Harris Poll**: Former component of BCS system
- **Computer Rankings**: Various algorithmic rankings

## Response Format

### Rankings Data Structure
```json
{
  "season": 2024,
  "season_type": "postseason",
  "week": 1,
  "polls": [
    {
      "poll": "AP Top 25",
      "ranks": [
        {
          "rank": 1,
          "school": "Ohio State",
          "conference": "Big Ten",
          "first_place_votes": 56,
          "points": 1400
        }
      ]
    }
  ]
}
```

### Key Fields
- **season**: Year of rankings
- **season_type**: Regular season or postseason
- **week**: Week number within season
- **poll**: Name of polling organization
- **rank**: Team's ranking position (1-25 typically)
- **school**: Team/school name
- **conference**: Conference affiliation
- **first_place_votes**: Number of first-place votes received
- **points**: Total polling points

### Ranking Positions
- **Top 10**: Elite teams with playoff/championship aspirations
- **11-25**: Ranked teams with bowl game implications
- **Others Receiving Votes**: Teams just outside rankings
- **Unranked**: Teams not receiving ranking consideration

## Running the Test

### Command
```bash
python rankings.py
```

### Expected Output
1. **Test Results**: Each poll with ranking period counts
2. **Poll Breakdown**: Rankings by polling organization
3. **Top Teams**: Top 5-10 teams from each poll
4. **JSON Export**: Complete results saved to `rankings.json`

### Success Indicators
- ✅ All 3 test cases return ranking data
- ✅ Multiple polls found for each time period
- ✅ Complete ranking information with points/votes
- ✅ JSON file created with detailed results

## Sample Rankings Output

### 2024 Final AP Top 25 (Sample)
```
🗳️  AP Top 25 (Top 5):
   1. Ohio State (Big Ten) - 1400 pts (56 1st)
   2. Notre Dame (FBS Independents) - 1342 pts
   3. Oregon (Big Ten) - 1255 pts
   4. Texas (SEC) - 1211 pts
   5. Penn State (Big Ten) - 1203 pts
```

### Conference Representation
- **SEC**: Multiple teams typically in top 25
- **Big Ten**: Strong representation in rankings
- **Big 12**: Several ranked teams
- **ACC**: Competitive conference presence
- **Group of 5**: Occasional ranked teams

## JSON Output File

### File: `rankings.json`
Contains complete test results including:
- **Test metadata**: Timestamps, server URL, test names
- **HTTP responses**: Full MCP server responses
- **Extracted data**: Complete ranking information
- **Summary statistics**: Poll counts, ranking periods
- **Sample data**: Top teams from each poll

### Sample JSON Structure
```json
{
  "test_name": "CFB Rankings MCP Test",
  "timestamp": "2025-08-15T00:35:45.456789",
  "server_url": "https://cfbmcp-production.up.railway.app/mcp",
  "tests": [
    {
      "name": "2024 Final Rankings",
      "tool": "getCFBRankings",
      "args": {"year": 2024, "week": 15},
      "success": true,
      "summary": {
        "ranking_periods": 1,
        "total_polls": 4,
        "polls": [
          {
            "poll_name": "AP Top 25",
            "teams_count": 25,
            "top_5": [...]
          }
        ]
      }
    }
  ]
}
```

## Use Cases

### 1. Playoff Analysis
- Track College Football Playoff rankings evolution
- Analyze playoff selection criteria and bubble teams
- Compare committee rankings vs traditional polls

### 2. Conference Strength
- Evaluate conference representation in rankings
- Track conference performance throughout season
- Analyze inter-conference ranking comparisons

### 3. Historical Analysis
- Compare preseason vs final rankings
- Track team ranking trajectories throughout season
- Analyze ranking volatility and consistency

### 4. Poll Comparison
- Compare different polling methodologies
- Analyze voter bias and regional preferences
- Track consensus vs outlier rankings

## Ranking Analysis

### Voting Patterns
- **First Place Votes**: Concentration vs distribution
- **Point Totals**: Margin between ranked teams
- **Consensus**: Agreement between different polls
- **Volatility**: Week-to-week ranking changes

### Conference Analysis
- **Representation**: Number of teams per conference
- **Depth**: Multiple ranked teams from same conference
- **Strength**: Average ranking of conference teams
- **Bias**: Regional or historical voting preferences

### Seasonal Trends
- **Preseason Hype**: Teams ranked high early
- **Risers**: Teams climbing throughout season
- **Fallers**: Teams dropping from early rankings
- **Consistency**: Teams maintaining rankings

## Error Handling

### Common Issues
- **Historical data limits**: Some years may have limited polls
- **Week availability**: Not all weeks have rankings
- **Poll variations**: Different polls available by year
- **Network timeouts**: 30-second timeout for requests

### Troubleshooting
1. **Check year validity**: Ensure year has ranking data
2. **Verify week numbers**: Confirm week has published rankings
3. **Review season types**: Regular vs postseason availability
4. **Handle missing polls**: Some polls may not exist for all periods

## Integration

### With Game Data
Combine rankings with game results to analyze ranked vs unranked matchups and their impact on rankings.

### With Team Stats
Cross-reference rankings with team performance statistics to understand ranking criteria.

### With Conference Data
Analyze conference strength and representation in national rankings.

### Data Export
JSON output can be imported into:
- Playoff prediction models
- Conference strength analysis tools
- Historical ranking databases
- Voting pattern analysis systems
- College football prediction markets

Perfect for college football ranking analysis and playoff prediction! 🏆🏈