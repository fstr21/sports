#!/usr/bin/env python3
"""
Scheduler for Daily WNBA Analysis
Runs analysis automatically and manages output files efficiently.
"""

import schedule
import time
import os
from datetime import datetime, timedelta
from daily_wnba_analyzer import WNBAAnalyzer
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wnba_analyzer.log'),
        logging.StreamHandler()
    ]
)

class DailyScheduler:
    def __init__(self):
        self.analyzer = WNBAAnalyzer()
        self.output_dir = "daily_reports"
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def run_daily_analysis(self):
        """Run the daily analysis job."""
        try:
            logging.info("🏀 Starting daily WNBA analysis...")
            
            # Process today's games
            analyses = self.analyzer.process_daily_games()
            
            if not analyses:
                logging.info("No games found for today.")
                return
            
            # Generate report
            report = self.analyzer.generate_daily_report(analyses)
            
            # Save to dated file
            date_str = datetime.now().strftime('%Y%m%d')
            filename = os.path.join(self.output_dir, f"wnba_analysis_{date_str}.md")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Also create/update "latest" file for easy access
            latest_file = os.path.join(self.output_dir, "latest_analysis.md")
            with open(latest_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logging.info(f"✅ Analysis complete! {len(analyses)} games processed")
            logging.info(f"📄 Report saved to {filename}")
            
            # Log strong betting opportunities
            strong_bets = [a for a in analyses if a['betting_recommendation']['strength'] == 'STRONG']
            if strong_bets:
                logging.info(f"🎯 {len(strong_bets)} STRONG betting opportunities found!")
                for bet in strong_bets:
                    logging.info(f"   - {bet['matchup']}: {bet['betting_recommendation']['primary_bet']}")
            
        except Exception as e:
            logging.error(f"❌ Error during daily analysis: {str(e)}")
    
    def cleanup_old_reports(self, days_to_keep=30):
        """Clean up old report files to save space."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(self.output_dir):
                if filename.startswith("wnba_analysis_") and filename.endswith(".md"):
                    # Extract date from filename
                    date_str = filename.replace("wnba_analysis_", "").replace(".md", "")
                    try:
                        file_date = datetime.strptime(date_str, "%Y%m%d")
                        if file_date < cutoff_date:
                            file_path = os.path.join(self.output_dir, filename)
                            os.remove(file_path)
                            logging.info(f"🗑️ Cleaned up old report: {filename}")
                    except ValueError:
                        continue  # Skip files that don't match date format
                        
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
    
    def run_test_analysis(self, date=None):
        """Run analysis for a specific date (for testing)."""
        try:
            test_date = date or datetime.now().strftime("%Y%m%d")
            logging.info(f"🧪 Running test analysis for {test_date}")
            
            analyses = self.analyzer.process_daily_games(test_date)
            
            if analyses:
                report = self.analyzer.generate_daily_report(analyses, test_date)
                
                # Save test report
                filename = f"test_analysis_{test_date}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                logging.info(f"✅ Test analysis complete! Report saved to {filename}")
                return True
            else:
                logging.info("No games found for test date.")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error during test analysis: {str(e)}")
            return False

def main():
    """Main scheduler function."""
    scheduler = DailyScheduler()
    
    # Schedule daily analysis
    # Run at 10 AM every day (games are usually evening, so morning gives us fresh data)
    schedule.every().day.at("10:00").do(scheduler.run_daily_analysis)
    
    # Weekly cleanup on Sundays at 2 AM
    schedule.every().sunday.at("02:00").do(scheduler.cleanup_old_reports)
    
    logging.info("📅 WNBA Daily Analyzer Scheduler started")
    logging.info("⏰ Daily analysis scheduled for 10:00 AM")
    logging.info("🧹 Weekly cleanup scheduled for Sundays at 2:00 AM")
    
    # Run once immediately for testing
    logging.info("🚀 Running initial analysis...")
    scheduler.run_daily_analysis()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()