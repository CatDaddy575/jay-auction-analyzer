#!/usr/bin/env python3
"""
Test scraper on a live BringATrailer auction
"""

import sys
import sqlite3
from datetime import datetime
from src.config.credentials import get_credentials
from src.browser.launcher import BrowserManager
from src.scraper.auctions import AuctionScraper
from src.db.database import init_database

def test_scrape_auction(auction_url):
    """Test scraping a live auction"""

    print(f'🔧 Testing scraper on: {auction_url}\n')

    try:
        # Initialize
        init_database()

        # Launch browser
        print('🌐 Launching browser...')
        browser = BrowserManager()
        browser.launch()

        # Login
        print('🔐 Logging in...')
        if not browser.login():
            print('❌ Login failed')
            browser.close()
            return False

        print(f'✓ Logged in\n')

        # Navigate to auction
        print(f'📄 Navigating to auction...')
        html = browser.get_auction_page(auction_url)
        print(f'✓ Page loaded ({len(html)} bytes)\n')

        # Scrape data
        print('🔍 Scraping auction data...')
        scraper = AuctionScraper()
        result = scraper.parse_auction_page(html)

        auction_data = result['auction_data']
        bidding_history = result['bidding_history']

        # Display results
        print('\n' + '='*50)
        print('AUCTION DATA')
        print('='*50)
        print(f"Title: {auction_data['title']}")
        print(f"Asking Price: ${auction_data['asking_price']:,}")
        print(f"Current Bid: ${auction_data['current_bid']:,}")
        print(f"Bid Count: {auction_data['bid_count']}")
        print(f"Ends At: {auction_data['ends_at']}")
        print(f"Description: {auction_data['description'][:100]}..." if auction_data['description'] else "Description: (none)")

        print('\n' + '='*50)
        print(f'BIDDING HISTORY ({len(bidding_history)} bids)')
        print('='*50)

        if bidding_history:
            for i, bid in enumerate(bidding_history[:10], 1):  # Show first 10
                print(f"{i}. {bid['bidder']} - ${bid['amount']:,} at {bid['timestamp']}")
            if len(bidding_history) > 10:
                print(f"... and {len(bidding_history) - 10} more bids")
        else:
            print("(No bidding history found)")

        # Save to database
        print('\n' + '='*50)
        print('SAVING TO DATABASE')
        print('='*50)

        conn = sqlite3.connect('./data/jay.db')
        cursor = conn.cursor()

        # Extract auction ID from URL
        auction_id = auction_url.split('/')[-2] if '/' in auction_url else 'test-auction'

        # Insert auction
        cursor.execute('''
            INSERT OR REPLACE INTO auctions
            (ba_id, title, current_bid, bid_count, asking_price, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            auction_id,
            auction_data['title'],
            auction_data['current_bid'],
            auction_data['bid_count'],
            auction_data['asking_price'],
            'active',
            datetime.now().isoformat()
        ))

        # Insert bidders and history
        for bid in bidding_history:
            bidder = bid['bidder']

            # Insert/update bidder
            cursor.execute('''
                INSERT OR IGNORE INTO bidders (username)
                VALUES (?)
            ''', (bidder,))

            # Get bidder ID
            cursor.execute('SELECT id FROM bidders WHERE username = ?', (bidder,))
            bidder_id = cursor.fetchone()[0]

            # Insert bid
            cursor.execute('''
                INSERT INTO bidding_history
                (auction_id, bidder_username, bid_amount, bid_time, bid_position)
                VALUES ((SELECT id FROM auctions WHERE ba_id = ?), ?, ?, ?, ?)
            ''', (auction_id, bidder, bid['amount'], bid['timestamp'], 0))

        conn.commit()
        conn.close()

        print(f'✓ Saved auction to database')
        print(f'✓ Saved {len(bidding_history)} bids\n')

        # Close browser
        browser.close()

        print('✅ TEST COMPLETE')
        print(f'\nNow you can run: python main.py --monitor')
        print('to watch this auction with adaptive monitoring.\n')

        return True

    except Exception as error:
        print(f'\n❌ Error: {error}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Test URL
    auction_url = 'https://bringatrailer.com/listing/2021-ford-f-150-roush/'

    success = test_scrape_auction(auction_url)
    sys.exit(0 if success else 1)
