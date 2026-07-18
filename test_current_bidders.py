#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.bidder.current_bidders import CurrentBiddersAnalyzer

print('Testing Current Bidders Analyzer\n')
print('=' * 70)

analyzer = CurrentBiddersAnalyzer()

# Test with bidders from the 1979 Ford auction
test_bidders = ['JSpringer', 'bidder_892', 'bidder_156']

print(f'\nAnalyzing {len(test_bidders)} current bidders...\n')

competitors = analyzer.analyze_auction_competitors(test_bidders, estimated_market_value=32500)

print('=' * 70)
print('\nCOMPETITOR ANALYSIS:\n')

for i, competitor in enumerate(competitors, 1):
    if competitor:
        print(f'{i}. {competitor["bidder_name"]}')
        print(f'   Win Rate: {competitor["stats"]["win_rate"]}%')
        print(f'   Total Bids: {competitor["stats"]["total_bids"]}')
        print(f'   Total Wins: {competitor["stats"]["total_wins"]}')
        print(f'   Bidder Type: {competitor["bidder_type"]}')
        print(f'   Threat Level: {competitor["threat_level"]}/100')
        print(f'   Recommendation: {competitor["recommendation"]}')
        print()

print('=' * 70)
print('TEST COMPLETE')
