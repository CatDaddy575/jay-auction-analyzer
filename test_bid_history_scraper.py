#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.scraper.bid_history import BidHistoryScraper

url = 'https://bringatrailer.com/listing/2006-jaguar-xk8-convertible-27/'

print('Testing Bid History Scraper')
print('=' * 70)
print(f'URL: {url}\n')

scraper = BidHistoryScraper()

try:
    print('Extracting bid history with Playwright...\n')
    bidders = scraper.get_top_bidders(url, limit=10)

    print(f'Top bidders found: {len(bidders)}\n')
    print('-' * 70)

    for i, bidder in enumerate(bidders, 1):
        print(f'{i}. {bidder["bidder_name"]}')
        print(f'   Result: {bidder["result"]}')

    print('\n' + '=' * 70)
    print('Done!')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

finally:
    scraper.cleanup()
