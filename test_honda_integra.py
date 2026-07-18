#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.scraper.bid_history import BidHistoryScraper
from src.bidder.current_bidders import CurrentBiddersAnalyzer

url = 'https://bringatrailer.com/listing/1999-honda-integra-6/'

print('Testing Honda Integra Auction')
print('=' * 70)
print(f'URL: {url}\n')

bid_scraper = BidHistoryScraper()

try:
    print('Extracting bidders...\n')
    top_bidders = bid_scraper.get_top_bidders(url, limit=10)
    bid_scraper.cleanup()

    print(f'Bidders found: {len(top_bidders)}\n')

    if top_bidders:
        for i, bidder in enumerate(top_bidders, 1):
            print(f'{i}. {bidder["bidder_name"]}')

        print('\n' + '=' * 70)
        print('ANALYZING THREATS\n')

        bidder_names = [b['bidder_name'] for b in top_bidders]
        analyzer = CurrentBiddersAnalyzer()
        competitors = analyzer.analyze_auction_competitors(bidder_names, estimated_market_value=50000)

        for comp in competitors:
            if comp:
                print(f"{comp['bidder_name']}: Threat {comp['threat_level']}/100")
    else:
        print('NO BIDDERS FOUND - THIS IS A PROBLEM')

    print('\n' + '=' * 70)

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
