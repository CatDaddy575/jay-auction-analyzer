#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.bidder.current_bidders import CurrentBiddersAnalyzer
import requests
from bs4 import BeautifulSoup
import re

print('Testing Jay with a Different Auction\n')
print('=' * 70)

# Try a different auction - 1976 Ford F-100
auction_url = "https://bringatrailer.com/listing/1976-ford-f-100-ranger-xlt-4x4-w-dump-bed-11/"

print(f'Fetching auction: {auction_url}\n')

try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(auction_url, headers=headers, timeout=10)
    html = response.text

    # Extract bidder names
    soup = BeautifulSoup(html, 'html.parser')
    member_links = soup.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))

    bidder_names = set()
    for link in member_links:
        bidder_text = link.get_text(strip=True)
        if bidder_text and len(bidder_text) > 1 and len(bidder_text) < 50:
            bidder_names.add(bidder_text)

    bidder_list = list(bidder_names)

    print(f'Found {len(bidder_list)} bidders on this auction:')
    for i, bidder in enumerate(bidder_list[:10], 1):
        print(f'  {i}. {bidder}')

    if len(bidder_list) > 10:
        print(f'  ... and {len(bidder_list) - 10} more')

    print('\n' + '=' * 70)
    print('ANALYZING COMPETITORS\n')

    # Analyze all bidders
    analyzer = CurrentBiddersAnalyzer()
    competitors = analyzer.analyze_auction_competitors(bidder_list, estimated_market_value=25000)

    # Show results
    high_threat = [c for c in competitors if c and c['threat_level'] > 50]
    low_threat = [c for c in competitors if c and c['threat_level'] <= 50]

    print(f'HIGH THREAT ({len(high_threat)} bidders):')
    for comp in high_threat[:5]:
        if comp:
            print(f"\n  {comp['bidder_name']}")
            print(f'    Win Rate: {comp["stats"]["win_rate"]}%')
            print(f'    Threat: {comp["threat_level"]}/100')
            print(f'    Type: {comp["bidder_type"]}')
            print(f'    → {comp["recommendation"]}')

    print(f'\n\nLOW THREAT ({len(low_threat)} bidders):')
    for comp in low_threat[:5]:
        if comp:
            print(f"\n  {comp['bidder_name']}")
            print(f'    Win Rate: {comp["stats"]["win_rate"]}%')
            print(f'    Threat: {comp["threat_level"]}/100')

    print('\n' + '=' * 70)
    print('TEST COMPLETE - Go to https://jay-auction-analyzer.streamlit.app to see live')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
