#!/usr/bin/env python
# -*- coding: utf-8 -*-

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = 'https://bringatrailer.com/listing/2006-jaguar-xk8-convertible-27/'

print('Loading page with Playwright and analyzing...\n')

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()
page.goto(url, wait_until='domcontentloaded', timeout=30000)

try:
    page.wait_for_load_state('load', timeout=5000)
except:
    pass

html = page.content()
page.close()
browser.close()
playwright.stop()

soup = BeautifulSoup(html, 'html.parser')

# Find bid information
bid_info = soup.find('div', class_='bid-information-details')
print(f'bid-information-details found: {bool(bid_info)}\n')

if bid_info:
    # Get all member links in bid info section
    member_links = bid_info.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
    print(f'Member links in bid info: {len(member_links)}')
    for link in member_links:
        print(f'  - {link.get_text(strip=True)}')

# Also check full page for member links
print(f'\nAll member links on page:')
all_member_links = soup.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
print(f'Total: {len(all_member_links)}')

# Get unique bidders
seen = set()
for link in all_member_links:
    text = link.get_text(strip=True)
    if text and 1 < len(text) < 50 and text not in seen:
        seen.add(text)
        print(f'  - {text}')

# Look for bid comments or activity
print(f'\nSearching for bid comments/activity section...')
comments = soup.find_all('div', class_='comment')
print(f'Comments found: {len(comments)}')

# Check for specific bid information text
bid_text = soup.find('div', class_='bid-information')
if bid_text:
    text_content = bid_text.get_text()
    # Look for patterns like "bid by [name]" or "[name] placed bid"
    if 'bid' in text_content.lower():
        print('\nBid information text (first 500 chars):')
        print(text_content[:500])
