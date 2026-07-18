#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.scraper.bid_history import BidHistoryScraper
from src.bidder.current_bidders import CurrentBiddersAnalyzer

url = 'https://bringatrailer.com/listing/1989-porsche-928-s4-100/'

print('Testing Porsche 928 S4 Auction')
print('=' * 70)
print(f'URL: {url}\n')

# Extract bidders
print('Extracting bidders with Playwright...\n')
bid_scraper = BidHistoryScraper()

try:
    top_bidders = bid_scraper.get_top_bidders(url, limit=10)
    bid_scraper.cleanup()

    print(f'Top bidders found: {len(top_bidders)}\n')
    print('Bidder List:')
    print('-' * 70)

    for i, bidder in enumerate(top_bidders, 1):
        print(f'{i}. {bidder["bidder_name"]}')

    if top_bidders:
        print('\n' + '=' * 70)
        print('ANALYZING THREAT LEVELS\n')

        bidder_names = [b['bidder_name'] for b in top_bidders]
        analyzer = CurrentBiddersAnalyzer()
        competitors = analyzer.analyze_auction_competitors(bidder_names, estimated_market_value=80000)

        print('Bidder Analysis:')
        print('-' * 70)

        for comp in competitors:
            if comp:
                threat_icon = '🔴' if comp['threat_level'] > 75 else '🟠' if comp['threat_level'] > 50 else '🟢'
                print(f"\n{threat_icon} {comp['bidder_name']}")
                print(f'  Win Rate: {comp["stats"]["win_rate"]}%')
                print(f'  Threat: {comp["threat_level"]}/100')
                print(f'  Type: {comp["bidder_type"]}')

    print('\n' + '=' * 70)
    print('Ready to test on: https://jay-auction-analyzer.streamlit.app')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
