import schedule
import time
from datetime import datetime, timedelta
from src.browser.launcher import BrowserManager
from src.scraper.auctions import AuctionScraper
from src.db.database import get_connection
from src.monitor.tracker import AuctionMonitor
from src.strategy.engine import StrategyEngine

class AdaptiveMonitorScheduler:
    """
    Intelligently monitors auctions based on time remaining.

    Schedule:
    - 7+ days remaining: Check 1x per day
    - 2-7 days remaining: Check 2x per day
    - 24-48 hours remaining: Check every 2 hours
    - 2-24 hours remaining: Check every 15 minutes
    - <2 hours remaining: Check every 2-3 minutes (chaos zone)
    - <5 minutes: Real-time monitoring
    """

    def __init__(self, browser, scraper, monitor, strategy):
        self.browser = browser
        self.scraper = scraper
        self.monitor = monitor
        self.strategy = strategy
        self.db = get_connection()

        # Track last check times to avoid redundant checks
        self.last_checks = {}

        # Cache previous auction data to detect changes
        self.auction_cache = {}

    def determine_check_interval(self, hours_remaining):
        """Determine check interval in minutes based on time left"""
        if hours_remaining > 168:  # 7+ days
            return 1440  # Once per day
        elif hours_remaining > 48:  # 2-7 days
            return 720  # Twice per day
        elif hours_remaining > 24:  # 24-48 hours
            return 120  # Every 2 hours
        elif hours_remaining > 2:  # 2-24 hours
            return 15  # Every 15 minutes
        elif hours_remaining > 0.08:  # >5 minutes
            return 3  # Every 2-3 minutes
        else:  # <5 minutes
            return 0.5  # Real-time monitoring

    def should_check_auction(self, auction_id, hours_remaining):
        """Determine if auction should be checked now"""
        if auction_id not in self.last_checks:
            self.last_checks[auction_id] = datetime.now()
            return True

        interval_minutes = self.determine_check_interval(hours_remaining)
        last_check = self.last_checks[auction_id]
        time_since_check = (datetime.now() - last_check).total_seconds() / 60

        if time_since_check >= interval_minutes:
            self.last_checks[auction_id] = datetime.now()
            return True

        return False

    def check_auction(self, auction_id):
        """Check a single auction for changes"""
        try:
            cursor = self.db.cursor()

            # Get auction data from DB
            cursor.execute('SELECT ba_id, title, ends_at FROM auctions WHERE ba_id = ?', (auction_id,))
            result = cursor.fetchone()

            if not result:
                print(f'⚠️  Auction {auction_id} not in database')
                return False

            ba_id, title, ends_at_str = result

            # Calculate hours remaining
            if ends_at_str:
                ends_at = datetime.fromisoformat(ends_at_str)
                hours_remaining = (ends_at - datetime.now()).total_seconds() / 3600
            else:
                hours_remaining = 999  # Unknown, assume days remaining

            # Check if we should monitor this auction now
            if not self.should_check_auction(auction_id, hours_remaining):
                return False  # Not time to check yet

            # Get live auction data (would call browser scraper here)
            # For now, this is a placeholder
            print(f'🔍 Checking {title} ({ba_id})... {hours_remaining:.1f}h remaining')

            # In real implementation, would scrape live data here
            # current_data = self.scrape_live_auction(auction_id)
            # self.monitor.check_auction(auction_id, current_data)

            return True

        except Exception as e:
            print(f'❌ Error checking auction {auction_id}: {e}')
            return False

    def schedule_monitoring(self):
        """Set up monitoring jobs for all watched auctions"""
        cursor = self.db.cursor()
        cursor.execute('SELECT ba_id FROM auctions WHERE status = "active"')
        auctions = cursor.fetchall()

        if not auctions:
            print('📋 No active auctions to monitor')
            return

        print(f'📊 Scheduling monitoring for {len(auctions)} auction(s)')

        for (auction_id,) in auctions:
            # Schedule a job for this auction
            schedule.every(1).minutes.do(self.check_auction, auction_id)

        return True

    def run_scheduler(self):
        """Run the scheduler loop"""
        print('⏲️  Starting adaptive monitoring scheduler...')
        print('📌 Monitoring will adjust frequency based on time remaining\n')

        try:
            while True:
                # Run any scheduled tasks that are due
                schedule.run_pending()
                time.sleep(10)  # Check every 10 seconds if tasks are due

        except KeyboardInterrupt:
            print('\n⏹️  Scheduler stopped')
        finally:
            self.close()

    def close(self):
        """Clean up resources"""
        if self.db:
            self.db.close()
        if self.browser:
            self.browser.close()
