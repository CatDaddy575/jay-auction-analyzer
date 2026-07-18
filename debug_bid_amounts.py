#!/usr/bin/env python
# -*- coding: utf-8 -*-

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = 'https://bringatrailer.com/listing/1989-porsche-928-s4-100/'

print('Checking comment content for bid amounts...\n')

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
comments = soup.find_all('div', class_='comment')

print(f'Total comments: {len(comments)}\n')
print('First 5 comment texts:\n')

for i, comment in enumerate(comments[:5]):
    text = comment.get_text()
    print(f'Comment {i+1}:')
    print(f'{text[:200]}...\n')
