#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.bidder.profile_scraper import BidderProfileScraper
from src.bidder.analyzer import BidderBehaviorAnalyzer

print('Testing complete bidder profile flow...\n')
print('=' * 60)

scraper = BidderProfileScraper()

# First get stats from static HTML
print('\n1. Extracting stats from static HTML...')
profile = scraper.scrape_bidder_profile('JSpringer', use_playwright=False)

stats = profile['basic_stats']
print(f'   Bidder: {profile["bidder_name"]}')
print(f'   Bids: {stats["total_bids"]}')
print(f'   Wins: {stats["total_wins"]}')
print(f'   Member Since: {stats["member_since"]}')

# Now try with Playwright
print('\n2. Attempting to extract bid history with Playwright...')
try:
    profile_full = scraper.scrape_bidder_profile('JSpringer', use_playwright=True)
    bid_history = profile_full['bidding_history']
    print(f'   Bid history records: {len(bid_history)}')

    if bid_history:
        print(f'\n   Recent bids:')
        for bid in bid_history[:5]:
            print(f'   - {bid["listing_name"][:40]} @ ${bid["bid_amount"]:,} ({bid["result"]})')
    else:
        print('   No bid history extracted (Playwright may not have found the table)')
except Exception as e:
    print(f'   Playwright failed: {e}')
    bid_history = []

print('\n' + '=' * 60)

if stats['total_bids'] > 0:
    print('\n3. Running behavior analysis...')
    analyzer = BidderBehaviorAnalyzer()
    analysis = analyzer.analyze_profile(profile)

    if 'error' not in analysis:
        print(f'   Analysis complete!')
        print(f'   Win Rate: {analysis["basic_stats"]["win_rate_overall"]}%')
        print(f'   Motivation: {analysis["prediction"]["estimated_motivation"]}')
        print(f'   Risk Level: {analysis["risk_assessment"]["level"]}')
        print(f'\n   SUCCESS: Complete bidder profile system working!')
    else:
        print(f'   Analysis failed: {analysis["error"]}')
else:
    print('\nFAILED: No bids found')
