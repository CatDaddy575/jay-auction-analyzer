#!/usr/bin/env python3
"""
Simple scraper test using requests library (no browser needed)
"""

import sys
import sqlite3
import requests
from datetime import datetime
from src.scraper.auctions import AuctionScraper
from src.db.database import init_database

def test_scrape_with_requests(auction_url):
    """Test scraping using requests library"""

    print(f'Testing scraper on: {auction_url}\n')

    try:
        # Initialize database
        init_database()

        # Fetch page HTML
        print('Fetching auction page...')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(auction_url, headers=headers, timeout=10)
        response.raise_for_status()

        html = response.text
        print(f'Page fetched successfully ({len(html)} bytes)\n')

        # Scrape data
        print('Scraping auction data...')
        scraper = AuctionScraper()
        result = scraper.parse_auction_page(html)

        auction_data = result['auction_data']
        bidding_history = result['bidding_history']

        # Display results
        print('\n' + '='*60)
        print('AUCTION DATA')
        print('='*60)
        print(f"Title: {auction_data['title'] or '(not found)'}")
        print(f"Asking Price: ${auction_data['asking_price']:,}" if auction_data['asking_price'] else "Asking Price: (not found)")
        print(f"Current Bid: ${auction_data['current_bid']:,}" if auction_data['current_bid'] else "Current Bid: (not found)")
        print(f"Bid Count: {auction_data['bid_count']}")
        print(f"Ends At: {auction_data['ends_at'] or '(not found)'}")
        description = auction_data['description']
        if description:
            print(f"Description: {description[:80]}...")
        else:
            print("Description: (not found)")

        print('\n' + '='*60)
        print(f'BIDDING HISTORY ({len(bidding_history)} bids)')
        print('='*60)

        if bidding_history:
            for i, bid in enumerate(bidding_history[:15], 1):
                print(f"{i}. {bid['bidder']} - ${bid['amount']:,}")
            if len(bidding_history) > 15:
                print(f"... and {len(bidding_history) - 15} more bids")
        else:
            print("(No bidding history found - page structure may have changed)")

        # Save to database
        print('\n' + '='*60)
        print('SAVING TO DATABASE')
        print('='*60)

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
            auction_data['title'] or 'Unknown',
            auction_data['current_bid'],
            auction_data['bid_count'],
            auction_data['asking_price'],
            'active',
            datetime.now().isoformat()
        ))

        # Insert bidders and history
        for bid in bidding_history:
            bidder = bid['bidder']
            if not bidder:
                continue

            # Insert/update bidder
            cursor.execute('''
                INSERT OR IGNORE INTO bidders (username)
                VALUES (?)
            ''', (bidder,))

            # Insert bid
            cursor.execute('''
                INSERT INTO bidding_history
                (auction_id, bidder_username, bid_amount, bid_time, bid_position)
                VALUES ((SELECT id FROM auctions WHERE ba_id = ?), ?, ?, ?, ?)
            ''', (auction_id, bidder, bid['amount'], bid['timestamp'], 0))

        conn.commit()
        conn.close()

        print(f'Saved auction to database')
        print(f'Saved {len(bidding_history)} bids\n')

        print('='*60)
        print('TEST COMPLETE')
        print('='*60)
        print(f'\nNext step: Monitor this auction with:')
        print(f'  python main.py --monitor\n')

        return True

    except Exception as error:
        print(f'\nError: {error}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    auction_url = 'https://bringatrailer.com/listing/2021-ford-f-150-roush/'
    success = test_scrape_with_requests(auction_url)
    sys.exit(0 if success else 1)
