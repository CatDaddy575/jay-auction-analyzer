#!/usr/bin/env python
# -*- coding: utf-8 -*-

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

print('Rendering bidder profile with Playwright...\n')

url = "https://bringatrailer.com/member/JSpringer/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print('Loading page...')
    page.goto(url, wait_until='networkidle')
    page.wait_for_load_state('networkidle')

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    print(f'Rendered HTML size: {len(html)} bytes\n')

    # Save for inspection
    with open('rendered_with_playwright.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Saved to rendered_with_playwright.html\n')

    # Look for tables
    print('Searching for tables...')
    tables = soup.find_all('table')
    print(f'Found {len(tables)} tables')

    for i, table in enumerate(tables[:5]):
        rows = len(table.find_all('tr'))
        headers = [th.get_text(strip=True) for th in table.find_all('th')[:5]]
        print(f'{i+1}. Rows: {rows}, Headers: {headers}')

    # Look for any element with "bid" in text
    print('\nSearching for "bid" elements...')
    bid_elements = soup.find_all(['div', 'section'], class_=lambda x: x and 'bid' in x.lower() if x else False)
    print(f'Found {len(bid_elements)} elements with "bid" in class')

    # Look for listing links
    print('\nSearching for listing history...')
    listing_links = soup.find_all('a', href=lambda x: x and '/listing/' in (x if isinstance(x, str) else ''))
    print(f'Found {len(listing_links)} listing links')

    if listing_links:
        print('Sample listings:')
        for link in listing_links[1:6]:  # Skip first empty one
            print(f'  - {link.get_text(strip=True)[:50]}')

    browser.close()
    print('\nDone.')
