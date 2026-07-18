#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')

from src.bidder.profile_scraper import BidderProfileScraper
from src.bidder.analyzer import BidderBehaviorAnalyzer
import json

print('Testing Bidder Profile Analysis System\n')
print('=' * 60)

# Test with a real bidder from the 1979 Ford auction
bidder_name = 'JSpringer'

print(f'\nFetching profile for: {bidder_name}...')
scraper = BidderProfileScraper()
profile = scraper.scrape_bidder_profile(bidder_name)

if 'error' in profile:
    print(f'ERROR: {profile["error"]}')
else:
    print(f'✓ Profile fetched successfully')
    print(f'\nBasic Stats:')
    print(f'  - Total Bids: {profile["basic_stats"]["total_bids"]}')
    print(f'  - Total Wins: {profile["basic_stats"]["total_wins"]}')
    print(f'  - Member Since: {profile["basic_stats"]["member_since"]}')
    print(f'  - Bidding History Records: {len(profile["bidding_history"])}')

    if profile["bidding_history"]:
        print(f'\nRecent Bids:')
        for bid in profile["bidding_history"][:5]:
            print(f'  - {bid["listing_name"]} @ ${bid["bid_amount"]:,} ({bid["result"]})')

        # Analyze behavior
        print(f'\n' + '=' * 60)
        print('Analyzing Behavioral Patterns...')
        analyzer = BidderBehaviorAnalyzer()
        analysis = analyzer.analyze_profile(profile)

        if 'error' not in analysis:
            print(f'\n✓ Analysis Complete')

            print(f'\nBehavioral Profile:')
            behavioral = analysis['behavioral']
            print(f'  - Bid Style: {behavioral["bidding_style"]}')
            print(f'  - Bid Velocity: {behavioral["bid_velocity"]}')
            print(f'  - Max Historical Bid: ${behavioral["max_historical_bid"]:,}')
            print(f'  - Budget Discipline: {behavioral["budget_discipline"]}')

            print(f'\nVehicle Type Breakdown:')
            for vehicle_type, stats in analysis['segmentation']['by_vehicle_type'].items():
                if stats['bids'] > 0:
                    print(f'  - {vehicle_type}: {stats["wins"]}/{stats["bids"]} wins ({stats["win_rate"]}%)')

            print(f'\nPrice Range Breakdown:')
            for price_range, stats in analysis['segmentation']['by_price_range'].items():
                if stats['bids'] > 0:
                    print(f'  - {price_range}: {stats["wins"]}/{stats["bids"]} wins ({stats["win_rate"]}%)')

            print(f'\nPredictions:')
            prediction = analysis['prediction']
            print(f'  - Estimated Motivation: {prediction["estimated_motivation"]}')
            print(f'  - Bidding Strategy: {prediction["bidding_strategy"]}')

            print(f'\nRisk Assessment:')
            risk = analysis['risk_assessment']
            print(f'  - Risk Level: {risk["level"]}')
            print(f'  - Competitive Strength: {risk["competitive_strength"]}')
            print(f'  - {risk["recommendation"]}')

            print(f'\n' + '=' * 60)
            print('TEST COMPLETE')
        else:
            print(f'Analysis error: {analysis["error"]}')
    else:
        print('No bidding history found')
