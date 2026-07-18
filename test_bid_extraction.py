#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.scraper.bid_history import BidHistoryScraper

url = 'https://bringatrailer.com/listing/1989-porsche-928-s4-100/'

print('Testing bid amount extraction...\n')

scraper = BidHistoryScraper()
bidders = scraper.scrape_bid_history(url)

print(f'Bidders extracted: {len(bidders)}\n')
print('Bidder data with bid amounts:\n')
print(f"{'Rank':<6} {'Bidder':<20} {'Highest Bid':<15} {'Bid Count':<10}")
print('-' * 55)

for i, bidder in enumerate(bidders[:10], 1):
    print(f"{i:<6} {bidder['bidder_name']:<20} ${bidder.get('bid_amount', 0):<14,.0f} {bidder.get('bid_count', 0):<10}")

scraper.cleanup()
