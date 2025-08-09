# WNBA Daily Game Analyzer

An efficient, automated system for analyzing WNBA games daily with minimal API calls and token usage. Perfect for generating betting insights and game predictions programmatically.

## 🚀 Features

- **Efficient API Usage**: Minimizes ESPN API calls (typically 1 + N team calls per day)
- **Automated Daily Analysis**: Processes all games for any given day
- **Smart Betting Recommendations**: Confidence-based betting suggestions
- **Multiple Output Formats**: Markdown reports, JSON data, logs
- **Scheduled Execution**: Automatic daily runs with cleanup
- **Cost Effective**: Designed to minimize token usage and API costs

## 📊 What It Analyzes

- Team records (overall, home, away)
- Point differentials and scoring averages
- Recent form and streaks
- Head-to-head implications
- Home court advantage
- Confidence-based betting recommendations

## 🛠️ Installation

1. **Clone or download the files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📋 Usage

### Quick Analysis (Manual)

```bash
# Analyze today's games
python run_analysis.py

# Analyze specific date (YYYYMMDD format)
python run_analysis.py 20250805
```

### Automated Daily Runs

```bash
# Start the scheduler (runs daily at 10 AM)
python scheduler.py
```

### Using the Core Analyzer

```python
from daily_wnba_analyzer import WNBAAnalyzer

analyzer = WNBAAnalyzer()

# Get today's games
analyses = analyzer.process_daily_games()

# Generate report
report = analyzer.generate_daily_report(analyses)
print(report)
```

## 📁 Output Files

- `wnba_analysis_YYYYMMDD.md` - Daily analysis reports
- `daily_reports/latest_analysis.md` - Always contains the most recent analysis
- `wnba_analyzer.log` - System logs and errors

## 🎯 Betting Recommendations

The system provides confidence-based recommendations:

- **STRONG** ⭐⭐⭐⭐⭐ (80%+ confidence) - High conviction bets
- **MODERATE** ⭐⭐⭐⭐ (60-79% confidence) - Solid opportunities
- **LEAN** ⭐⭐⭐ (40-59% confidence) - Slight edge
- **AVOID** ⭐⭐ (<40% confidence) - Too close to call

## 💡 Efficiency Features

### Minimal API Calls

- **1 call** for daily scoreboard (all games)
- **N calls** for team stats (where N = unique teams playing)
- **Total**: Typically 6-12 API calls per day vs 100+ for naive approaches

### Smart Data Processing

- Extracts only essential stats needed for analysis
- Caches team data within single run
- Processes multiple games from single scoreboard call

### Token Optimization

- Focused analysis algorithms (no LLM calls needed)
- Structured output generation
- Minimal text processing

## 📈 Sample Output

```markdown
# WNBA Daily Analysis - 2025-08-05

## Games Summary

Total Games: 5

### Game 1: Dallas Wings @ New York Liberty

**Prediction**: Home team wins
**Confidence**: 100.0% ⭐⭐⭐⭐⭐
**Recommendation**: STRONG - Home team moneyline

**Key Stats**:

- Home: 18-10 (86.9 PPG, +5.8 diff)
- Away: 8-21 (82.1 PPG, -4.5 diff)
```

## ⚙️ Configuration

Edit `config.py` to customize:

- API settings and rate limiting
- Analysis weights and thresholds
- Output formats and directories
- Betting recommendation criteria

## 🔄 Automation Options

### Daily Scheduler

- Runs analysis every day at 10 AM
- Automatic cleanup of old reports
- Comprehensive logging

### Custom Scheduling

```python
import schedule
from daily_wnba_analyzer import WNBAAnalyzer

analyzer = WNBAAnalyzer()

# Custom schedule
schedule.every().day.at("09:00").do(analyzer.process_daily_games)
```

## 📊 Cost Comparison

**Traditional Approach** (per day):

- 50+ API calls for individual game data
- Multiple LLM calls for analysis
- High token usage for report generation
- **Cost**: $5-15 per day

**This System** (per day):

- 6-12 API calls total
- No LLM calls needed
- Minimal token usage
- **Cost**: $0.10-0.50 per day

## 🚨 Important Notes

- **ESPN API**: Free but rate-limited. Be respectful with requests
- **Betting**: This is for analysis only. Gamble responsibly
- **Data Accuracy**: Always verify important data independently
- **Updates**: WNBA schedule changes may require adjustments

## 🔧 Troubleshooting

### Common Issues

1. **Encoding Errors**: Files use UTF-8 encoding
2. **No Games Found**: Check date format (YYYYMMDD)
3. **API Errors**: ESPN API may be temporarily unavailable
4. **Permission Errors**: Ensure write permissions for output directory

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is for educational and personal use. Respect ESPN's API terms of service.

## 🤝 Contributing

Feel free to submit improvements, especially for:

- Additional betting markets
- Enhanced statistical analysis
- New output formats
- Performance optimizations

---

**Happy Analyzing! 🏀📊**
