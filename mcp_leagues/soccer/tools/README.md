# Soccer Analysis Tools

## Core Functionality

### 🎯 Primary Scripts

#### **`core/interactive_match_finder.py`** ⭐
- **Purpose**: Find upcoming matches across EPL, La Liga, and MLS
- **Features**: 
  - Interactive date selection
  - Multi-league search (EPL, La Liga, MLS)
  - Complete odds display (match winner, over/under, handicap)
  - Match selection for detailed analysis
- **Usage**: `python core/interactive_match_finder.py`

#### **`core/efficient_h2h_analyzer.py`** ⭐  
- **Purpose**: Comprehensive head-to-head analysis
- **Features**:
  - Recent form analysis (last 10 games per team)
  - Historical H2H statistics (106+ games)
  - Recent direct meetings between teams
  - Professional prediction analysis
- **Usage**: `python core/efficient_h2h_analyzer.py`

### 🛠️ Templates

#### **`templates/westham_recent_matches.py`**
- **Purpose**: Template for individual team analysis
- **Method**: Proven date-by-date search
- **Usage**: Customize team ID and dates for any team

#### **`templates/chelsea_recent_matches.py`**
- **Purpose**: Template for individual team analysis
- **Method**: Proven date-by-date search  
- **Usage**: Customize team ID and dates for any team

### 📚 Documentation

#### **`HEAD_TO_HEAD_ANALYSIS_GUIDE.md`**
- Complete methodology guide
- Data presentation formats
- Integration workflows
- Best practices

## Directory Structure

```
tools/
├── core/                    # Primary functionality
│   ├── interactive_match_finder.py
│   └── efficient_h2h_analyzer.py
├── templates/               # Reusable templates
│   ├── westham_recent_matches.py
│   └── chelsea_recent_matches.py
├── archive/                 # Deprecated/debug scripts
├── matches/                 # Match data tools
├── team/                   # Team data tools
├── season/                 # Season data tools
├── head_to_head/           # H2H data tools
└── standing/              # League standing tools
```

## Quick Start

1. **Find upcoming matches**:
   ```bash
   cd core
   python interactive_match_finder.py
   ```

2. **Analyze team matchup**:
   ```bash
   cd core  
   python efficient_h2h_analyzer.py
   ```

3. **Get team recent form**:
   ```bash
   cd templates
   # Customize team ID in script, then run
   python westham_recent_matches.py
   ```

## API Configuration

- **League IDs**: EPL (228), La Liga (297), MLS (168)
- **Date Format**: DD-MM-YYYY (e.g., "22-08-2025")
- **Team IDs**: West Ham (3059), Chelsea (2916)
- **Auth Token**: Embedded in scripts

## Key Features

✅ **Multi-league support** (EPL, La Liga, MLS)
✅ **Comprehensive odds** (1X2, O/U, Handicap)
✅ **Recent form analysis** (last 10 games)
✅ **Historical comparisons** (100+ games)
✅ **Professional presentation** (tables, charts)
✅ **Prediction confidence** (multiple data layers)

## Data Sources

- **SoccerDataAPI**: Match data, odds, team info
- **Head-to-Head endpoint**: Historical statistics  
- **Date-by-date search**: Most reliable recent form data
- **Multi-layer analysis**: Historical + Recent + Direct meetings