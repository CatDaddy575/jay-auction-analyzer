#!/usr/bin/env python3
"""
Debug script to inspect BringATrailer HTML structure
"""

import requests
from bs4 import BeautifulSoup
import json

auction_url = 'https://bringatrailer.com/listing/2021-ford-f-150-roush/'

print('Fetching page...')
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
response = requests.get(auction_url, headers=headers, timeout=10)
html = response.text

print(f'Page size: {len(html)} bytes\n')

soup = BeautifulSoup(html, 'html.parser')

# Look for common patterns
print('='*60)
print('SEARCHING FOR DATA PATTERNS')
print('='*60)

# Look for title
print('\n--- Looking for TITLE ---')
title_selectors = [
    soup.find('h1'),
    soup.find('h2'),
    soup.find(class_='title'),
    soup.find(class_='auction-title'),
    soup.find('meta', property='og:title'),
]
for sel in title_selectors:
    if sel:
        print(f'Found: {sel.name if hasattr(sel, "name") else type(sel)} = {str(sel)[:100]}')

# Look for prices
print('\n--- Looking for PRICES ---')
price_patterns = [
    soup.find_all(string=lambda text: '$' in str(text) if text else False),
]
for match in soup.find_all(string=lambda text: '$' in str(text) if text else False)[:10]:
    print(f'  ${match.strip()[:60]}')

# Look for bid data
print('\n--- Looking for BID DATA ---')
bid_patterns = soup.find_all('div', class_=lambda x: x and 'bid' in x.lower())
print(f'Found {len(bid_patterns)} elements with "bid" in class')

# Look for script tags with JSON
print('\n--- Looking for JSON DATA IN SCRIPTS ---')
scripts = soup.find_all('script', type='application/json')
print(f'Found {len(scripts)} JSON script tags')

for i, script in enumerate(scripts[:3]):
    content = script.string
    if content:
        try:
            data = json.loads(content)
            print(f'\nScript {i} contains JSON with keys: {list(data.keys())[:5]}')
            # Save first script to file for inspection
            if i == 0:
                with open('./debug_json.json', 'w') as f:
                    json.dump(data, f, indent=2)
                print('  (Saved to debug_json.json)')
        except:
            print(f'Script {i}: {content[:100]}...')

# Save full HTML for manual inspection
print('\n--- Saving full HTML ---')
with open('./debug_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved to debug_page.html')

print('\n✓ Debug complete. Check debug_page.html to see the real structure.')
