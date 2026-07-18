#!/usr/bin/env python3
"""
Jay - BringATrailer Auction Agent
Main entry point
"""

import sys
from src.config.credentials import get_credentials
from src.browser.launcher import BrowserManager
from src.scraper.auctions import AuctionScraper
from src.db.database import init_database, get_connection
from src.monitor.tracker import AuctionMonitor
from src.strategy.engine import StrategyEngine
from src.scheduler.monitor_scheduler import AdaptiveMonitorScheduler

def test_mode():
    """Test mode: verify setup without monitoring"""
    print('🤖 Jay - BringATrailer Agent (TEST MODE)\n')

    try:
        # Test credentials
        credentials = get_credentials()
        print(f'✓ Credentials loaded for user: {credentials["username"]}')

        # Initialize database
        init_database()

        # Launch browser
        browser = BrowserManager()
        browser.launch()

        # Test login
        if browser.login():
            print('\n✅ Setup verified! Jay is ready.\n')
            print('📋 Next steps:')
            print('1. ✓ Browser automation working')
            print('2. ✓ Database initialized')
            print('3. Add auctions to database to monitor')
            print('4. Run in monitor mode: python main.py --monitor\n')

        browser.close()

    except Exception as error:
        print(f'❌ Error: {error}')
        sys.exit(1)

def monitor_mode():
    """Monitor mode: run adaptive scheduler"""
    print('🤖 Jay - BringATrailer Agent (MONITOR MODE)\n')

    try:
        # Initialize
        credentials = get_credentials()
        print(f'✓ Logged in as: {credentials["username"]}')

        init_database()

        # Set up components
        browser = BrowserManager()
        browser.launch()
        browser.login()

        scraper = AuctionScraper()
        db = get_connection()
        monitor = AuctionMonitor(db)
        strategy = StrategyEngine(db)

        # Create scheduler
        scheduler = AdaptiveMonitorScheduler(browser, scraper, monitor, strategy)

        # Schedule monitoring jobs
        scheduler.schedule_monitoring()

        # Run scheduler
        scheduler.run_scheduler()

    except Exception as error:
        print(f'❌ Error: {error}')
        sys.exit(1)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Jay - BringATrailer Auction Agent')
    parser.add_argument('--monitor', action='store_true', help='Run in monitor mode (requires auctions in DB)')
    parser.add_argument('--test', action='store_true', help='Run in test mode (verify setup)')

    args = parser.parse_args()

    if args.monitor:
        monitor_mode()
    else:
        test_mode()

if __name__ == '__main__':
    main()
