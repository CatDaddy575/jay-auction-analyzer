#!/usr/bin/env python
# -*- coding: utf-8 -*-

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

print('Fetching and rendering auction page with Playwright...\n')

url = 'https://bringatrailer.com/listing/1979-ford-f-250-88/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle')
    page.wait_for_load_state('networkidle')

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    # Save rendered HTML for inspection
    with open('rendered_auction.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Saved rendered HTML ({len(html)} bytes)')

    # Search for bidder-related content
    print('\nSearching for bid-related sections...\n')

    # Look for "bid" text
    text = soup.get_text()
    bid_count = text.lower().count('bid')
    print(f'Page contains "bid": {bid_count} times')

    # Find sections with high density of bid-related content
    all_divs = soup.find_all('div')
    print(f'Total divs: {len(all_divs)}')

    # Look for divs that contain both bidder names and prices
    promising_divs = []
    for div in all_divs:
        div_text = div.get_text()
        if '$' in div_text and len(div_text) > 50 and len(div_text) < 500:
            if any(name in div_text for name in ['bidder', 'bid', 'amount', 'placed']):
                promising_divs.append({
                    'classes': div.get('class', []),
                    'text_preview': div_text[:100],
                    'length': len(div_text)
                })

    print(f'\nPromising divs with prices and bid-related text: {len(promising_divs)}')
    for i, div_info in enumerate(promising_divs[:5]):
        print(f'{i+1}. classes: {div_info["classes"]}')
        print(f'   text: {div_info["text_preview"]}...')
        print()

    # Look for any element containing bidder names we saw earlier
    bidder_mentions = soup.find_all(string=lambda x: x and 'JSpringer' in (x if isinstance(x, str) else ''))
    print(f'\nFound "JSpringer" mentions: {len(bidder_mentions)}')

    if bidder_mentions:
        for mention in bidder_mentions[:3]:
            parent = mention.parent
            print(f'Tag: {parent.name}, Classes: {parent.get("class", [])}')
            print(f'Text: {mention.strip()[:100]}\n')

    browser.close()
    print('\nRendered HTML saved to: rendered_auction.html')
