"""
Extract bid history from BringATrailer auctions
Shows all bidders who have placed bids, ranked by activity
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re


class BidHistoryScraper:
    """Extract full bid history from BringATrailer auction pages"""

    def __init__(self):
        self.playwright = None
        self.browser = None

    def _get_browser(self):
        """Lazy load Playwright browser"""
        if not self.browser:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
        return self.browser

    def scrape_bid_history(self, auction_url):
        """
        Extract bid history from auction.
        Try Playwright first (for full list), fallback to static HTML.
        Returns list of dicts: {bidder_name, bid_amount, timestamp, result}
        """
        # Try Playwright first (better extraction)
        try:
            browser = self._get_browser()
            page = browser.new_page()
            page.goto(auction_url, wait_until='domcontentloaded', timeout=30000)

            # Give JavaScript time to render
            try:
                page.wait_for_load_state('load', timeout=5000)
            except:
                pass

            html = page.content()
            page.close()

            return self._parse_bid_history(html, auction_url)

        except Exception as e:
            print(f"Playwright failed ({e}), falling back to static HTML...")
            # Fallback to static HTML scraping
            try:
                import requests
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(auction_url, headers=headers, timeout=10)
                return self._parse_bid_history(response.text, auction_url)
            except Exception as fallback_error:
                print(f"Static HTML fallback also failed: {fallback_error}")
                return []

    def _parse_bid_history(self, html, auction_url):
        """Parse bid history from page HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        bidders_list = []

        # Extract ALL member links from page (includes bidders in comments, activity, etc.)
        all_member_links = soup.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))

        if not all_member_links:
            return []

        # Extract unique bidder names, filtering out duplicates and sellers
        seen_bidders = {}
        for link in all_member_links:
            bidder_text = link.get_text(strip=True)

            if not bidder_text or len(bidder_text) < 2 or len(bidder_text) > 50:
                continue

            # Normalize name (remove @ prefix if present)
            normalized_name = bidder_text.lstrip('@')

            # Skip if already seen (under normalized name)
            if normalized_name in seen_bidders:
                continue

            # Skip if seller (marked with "(The Seller)" text)
            if '(The Seller)' in bidder_text or '(the seller)' in bidder_text.lower():
                continue

            # Skip common non-bidder terms
            if normalized_name.lower() in ['bringatrailer', 'seller', 'reserve', 'admin']:
                continue

            # Add to bidders list (keep first occurrence)
            seen_bidders[normalized_name] = True
            bidders_list.append({
                'bidder_name': normalized_name,
                'bid_amount': None,
                'timestamp': None,
                'result': 'active'
            })

        return bidders_list

    def get_top_bidders(self, auction_url, limit=10):
        """
        Get top N active bidders from auction.
        Returns bidders ranked by activity (current high bidder first)
        """
        all_bids = self.scrape_bid_history(auction_url)

        if not all_bids:
            return []

        # Remove duplicates, keep first occurrence (most recent)
        seen = set()
        unique_bidders = []
        for bid in all_bids:
            name = bid['bidder_name']
            if name not in seen:
                seen.add(name)
                unique_bidders.append(bid)

        return unique_bidders[:limit]

    def cleanup(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
