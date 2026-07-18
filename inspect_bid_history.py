#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

url = 'https://bringatrailer.com/listing/2006-jaguar-xk8-convertible-27/'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

print('Inspecting BringATrailer bid history structure...\n')
print('=' * 70)

# Look for bid-related sections
print('\nLooking for bid history elements:')
print('-' * 70)

# Check for common patterns
bid_history_div = soup.find('div', class_='bid-history')
bid_activity_div = soup.find('div', class_='bid-activity')
comments_section = soup.find('div', class_='comments')

print(f'bid-history div: {bool(bid_history_div)}')
print(f'bid-activity div: {bool(bid_activity_div)}')
print(f'comments section: {bool(comments_section)}')

# Find all divs with 'bid' in class
bid_divs = soup.find_all('div', class_=lambda x: x and 'bid' in x.lower())
print(f'All divs with "bid" in class: {len(bid_divs)}')
for div in bid_divs[:5]:
    cls = div.get('class', [])
    print(f'  - {cls}')

# Look for tables
tables = soup.find_all('table')
print(f'\nTables on page: {len(tables)}')
for i, table in enumerate(tables[:3]):
    print(f'  Table {i}: {table.get("class", [])}')

# Search for keywords in HTML
print(f'\nKeyword search in HTML:')
html_lower = response.text.lower()
print(f'  "bid history": {"bid history" in html_lower}')
print(f'  "bid activity": {"bid activity" in html_lower}')
print(f'  "bidder": {"bidder" in html_lower}')
print(f'  "bids placed": {"bids placed" in html_lower}')

# Look for comment structure (often where bids are listed)
print(f'\nComment sections:')
comments = soup.find_all('div', class_='comment')
print(f'  Comments found: {len(comments)}')

# Check for activity feed
activity = soup.find_all('div', class_=lambda x: x and ('activity' in str(x).lower() or 'feed' in str(x).lower()))
print(f'Activity/feed elements: {len(activity)}')

print('\n' + '=' * 70)
print('Analysis:')
if bid_history_div or bid_activity_div or len(comments) > 10:
    print('✓ Bid history structure FOUND - can be extracted')
else:
    print('✗ Bid history structure NOT visible in static HTML')
    print('  Solution: Need Playwright to render JavaScript-loaded bid history')
