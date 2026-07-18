#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.bidder.profile_scraper import BidderProfileScraper

print('Testing fixed bidder profile scraper...\n')

scraper = BidderProfileScraper()
profile = scraper.scrape_bidder_profile('JSpringer', use_playwright=False)

if 'error' in profile:
    print(f'ERROR: {profile["error"]}')
else:
    stats = profile['basic_stats']
    print(f'Bidder: {profile["bidder_name"]}')
    print(f'Total Bids: {stats["total_bids"]}')
    print(f'Total Wins: {stats["total_wins"]}')
    print(f'Comments: {stats["total_comments"]}')
    print(f'Listings: {stats["total_listings"]}')
    print(f'Member Since: {stats["member_since"]}')
    print(f'Bid History Records: {len(profile["bidding_history"])}')

    if stats['total_bids'] > 0:
        print('\nSUCCESS: Stats extracted correctly!')
    else:
        print('\nFAILED: Stats not extracted')
