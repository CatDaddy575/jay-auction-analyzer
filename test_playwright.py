#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.scraper.auctions import AuctionScraper
import requests

print('Testing improved Playwright extraction...\n')

url = 'https://bringatrailer.com/listing/1979-ford-f-250-88/'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    html = response.text

    scraper = AuctionScraper()
    result = scraper.parse_auction_page(html, url=url)

    auction_data = result['auction_data']
    bidding_history = result['bidding_history']

    print(f'Auction: {auction_data["title"]}')
    print(f'Current Bid: ${auction_data["current_bid"]:,}')
    print(f'Extracted: {len(bidding_history)} bids\n')

    if bidding_history:
        print('First 5 bids:')
        for i, bid in enumerate(bidding_history[:5], 1):
            print(f'  {i}. {bid["bidder"]:<25} ${bid["amount"]:>8,}')
        print(f'\nTEST PASSED: Successfully extracted {len(bidding_history)} bids')
    else:
        print('TEST FAILED: No bids extracted')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
