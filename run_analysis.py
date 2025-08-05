#!/usr/bin/env python3
"""
CLI tool for running WNBA analysis
Usage: python run_analysis.py [date]
"""

import sys
from datetime import datetime
from daily_wnba_analyzer import WNBAAnalyzer

def main():
    """Run analysis with optional date parameter."""
    
    # Parse command line arguments
    date = None
    if len(sys.argv) > 1:
        date_arg = sys.argv[1]
        try:
            # Validate date format
            datetime.strptime(date_arg, "%Y%m%d")
            date = date_arg
        except ValueError:
            print("❌ Invalid date format. Use YYYYMMDD (e.g., 20250805)")
            sys.exit(1)
    
    # Run analysis
    analyzer = WNBAAnalyzer()
    
    print("🏀 WNBA Game Analyzer")
    print("=" * 50)
    
    try:
        analyses = analyzer.process_daily_games(date)
        
        if not analyses:
            print("No games found for the specified date.")
            return
        
        # Generate and save report
        report = analyzer.generate_daily_report(analyses, date)
        
        # Create filename
        report_date = date or datetime.now().strftime("%Y%m%d")
        filename = f"wnba_analysis_{report_date}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Analysis complete!")
        print(f"📊 Processed {len(analyses)} games")
        print(f"📄 Report saved to: {filename}")
        
        # Show summary
        print("\n🎯 Betting Opportunities:")
        for analysis in analyses:
            rec = analysis['betting_recommendation']
            stars = "⭐" * rec['stars']
            print(f"  {analysis['matchup']}: {rec['strength']} {stars}")
        
        # Count strong bets
        strong_bets = [a for a in analyses if a['betting_recommendation']['strength'] == 'STRONG']
        if strong_bets:
            print(f"\n🔥 {len(strong_bets)} STRONG betting opportunities found!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()