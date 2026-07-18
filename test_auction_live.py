#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.bidder.current_bidders import CurrentBiddersAnalyzer
import requests
from bs4 import BeautifulSoup

print('Testing Jay Bidder Analysis - Live Auction\n')
print('=' * 70)

# Test with the 1979 Ford F-250 we know works
url = 'https://bringatrailer.com/listing/1979-ford-f-250-88/'

print(f'Testing: 1979 Ford F-250')
print(f'URL: {url}\n')

try:
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get bidders
    member_links = soup.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
    bidder_names = set()
    for link in member_links:
        text = link.get_text(strip=True)
        if text and 1 < len(text) < 50:
            bidder_names.add(text)

    bidders = list(bidder_names)[:10]

    print(f'Bidders found: {len(bidders)}')
    for bidder in bidders:
        print(f'  - {bidder}')

    print('\n' + '=' * 70)
    print('COMPETITOR ANALYSIS\n')

    # Analyze
    analyzer = CurrentBiddersAnalyzer()
    comps = analyzer.analyze_auction_competitors(bidders, 32500)

    print('{:<20} | {:>8} | {:>10} | {:<25}'.format('Bidder', 'Win %', 'Threat', 'Type'))
    print('-' * 70)

    for c in comps:
        if c:
            print('{:<20} | {:>7}% | {:>9}/100 | {:<25}'.format(
                c['bidder_name'],
                c['stats']['win_rate'],
                c['threat_level'],
                c['bidder_type']
            ))

    print('\n' + '=' * 70)
    print('SUCCESS: Bidder analysis working!')
    print('=' * 70)
    print('\nGo to: https://jay-auction-analyzer.streamlit.app')
    print('Paste this URL to test live in the web interface')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
