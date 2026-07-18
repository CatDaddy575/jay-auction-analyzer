#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.bidder.current_bidders import CurrentBiddersAnalyzer

url = 'https://bringatrailer.com/listing/2006-jaguar-xk8-convertible-27/'
bidders = ['Bigjumpus', 'valeurosport']

print('Testing Jaguar XK8 Auction')
print('=' * 70)
print(f'URL: {url}')
print(f'Current Bid: $13,500')
print(f'Bidders: {bidders}\n')

analyzer = CurrentBiddersAnalyzer()
competitors = analyzer.analyze_auction_competitors(bidders, estimated_market_value=28000)

print('Competitor Analysis:')
print('-' * 70)

for comp in competitors:
    if comp:
        print(f"\n{comp['bidder_name']}")
        print(f"  Win Rate: {comp['stats']['win_rate']}%")
        print(f"  Total Bids: {comp['stats']['total_bids']}")
        print(f"  Total Wins: {comp['stats']['total_wins']}")
        print(f"  Threat Level: {comp['threat_level']}/100")
        print(f"  Type: {comp['bidder_type']}")
        print(f"  Recommendation: {comp['recommendation']}")
    else:
        print(f"\nFailed to analyze")

print('\n' + '=' * 70)
print('Done. Try the auction URL in Jay at:')
print('https://jay-auction-analyzer.streamlit.app')
