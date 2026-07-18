#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import re

url = 'https://bringatrailer.com/listing/1999-honda-integra-6/'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, 'html.parser')

print('Looking for embedded JSON data...\n')
print('=' * 70)

# Search for script tags with JSON data
scripts = soup.find_all('script', type='application/json')
print(f'JSON script tags found: {len(scripts)}\n')

for i, script in enumerate(scripts[:3]):
    print(f'Script {i+1}:')
    try:
        data = json.loads(script.string)
        # Print first 200 chars of what's in there
        print(f'  Keys: {list(data.keys())[:5]}')
        print(f'  Content preview: {str(data)[:200]}...\n')
    except:
        print(f'  Could not parse as JSON\n')

# Also look for JSON in regular script tags
regular_scripts = soup.find_all('script')
print(f'\nTotal script tags: {len(regular_scripts)}')

# Search for specific patterns in scripts
for i, script in enumerate(regular_scripts):
    if script.string and 'bid' in script.string.lower():
        print(f'\nScript {i} mentions "bid":')
        print(script.string[:300])
        break

# Look for data attributes
print('\n' + '=' * 70)
print('Searching for data attributes...\n')

# Check for data-auction or similar attributes
elements_with_data = soup.find_all(attrs={'data-auction': True})
print(f'Elements with data-auction: {len(elements_with_data)}')

# BringATrailer might use Knockout.js or similar - look for bid data binding
bid_elements = soup.find_all(attrs={'data-bind': lambda x: x and 'bid' in x.lower() if x else False})
print(f'Elements with data-bind containing "bid": {len(bid_elements)}')

for elem in bid_elements[:2]:
    print(f'  {elem.name}: {elem.get("data-bind")}')
