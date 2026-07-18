#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

url = 'https://bringatrailer.com/listing/1999-honda-integra-6/'

print('Testing STATIC HTML fallback (no Playwright)\n')
print('=' * 70)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

# Check for comments in static HTML
comments = soup.find_all('div', class_='comment')
print(f'Comments found in static HTML: {len(comments)}')

# Check for bid information
bid_info = soup.find('div', class_='bid-information')
print(f'Bid information div found: {bool(bid_info)}')

if bid_info:
    member_links = bid_info.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
    print(f'Member links in bid-information: {len(member_links)}')
    for link in member_links:
        print(f'  - {link.get_text(strip=True)}')

# Check for any member links related to bids
print(f'\nSearching HTML for "bid" content...')
html_text = response.text.lower()
if 'bids placed' in html_text:
    print('✓ Found "bids placed" in HTML')
if 'bid history' in html_text:
    print('✓ Found "bid history" in HTML')
if 'bidders' in html_text:
    print('✓ Found "bidders" in HTML')

# Try finding all member links
all_member_links = soup.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
print(f'\nAll member links on page: {len(all_member_links)}')
print('\nFirst 15 names:')
seen = set()
count = 0
for link in all_member_links:
    text = link.get_text(strip=True).lstrip('@')
    if text and text not in seen and len(text) > 2 and len(text) < 50:
        seen.add(text)
        print(f'  - {text}')
        count += 1
        if count >= 15:
            break

print('\n' + '=' * 70)
print('CONCLUSION:')
if len(comments) == 0:
    print('❌ Comments NOT in static HTML (JavaScript-rendered)')
    print('   Static fallback will NOT work for this page')
else:
    print('✓ Comments found in static HTML')
