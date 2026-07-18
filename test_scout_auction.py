#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from src.scraper.bid_history import BidHistoryScraper

url = 'https://bringatrailer.com/listing/1964-international-harvester-scout-80-36/'

print('Testing Scout 80 auction...\n')
print('='*70)

scraper = BidHistoryScraper()
bidders = scraper.get_top_bidders(url, limit=10)

print(f'Bidders extracted: {len(bidders)}\n')
print(f"{'Rank':<6} {'Bidder':<20} {'Highest Bid':<15} {'Bid Count':<12} {'Latest Bid Time':<25}")
print('-' * 80)

for i, bidder in enumerate(bidders[:15], 1):
    bid_amt = f"${bidder.get('bid_amount', 0):,.0f}" if bidder.get('bid_amount') else '$0'
    latest_time = bidder.get('latest_time') or 'N/A'
    print(f"{i:<6} {bidder['bidder_name']:<20} {bid_amt:<15} {bidder.get('bid_count', 0):<12} {latest_time:<25}")

print('\n' + '='*70)
print('Expected from your screenshot:')
print('Bobby21 - $9,999')
print('Classichondaman - $8,600')
print('c2girl - $8,500')
print('ccpanel - $8,200')
print('Seanangus2316 - $8,080')
print('Vxviper10 - $5,100')

scraper.cleanup()
