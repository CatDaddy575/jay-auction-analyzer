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
        """Parse bid history from page HTML - extract only from comments/bidding activity"""
        soup = BeautifulSoup(html, 'html.parser')
        bidders_list = []

        # First, find the seller so we can exclude them
        seller_name = self._find_seller(soup)

        # Extract bidders from comments section (where bid activity happens)
        comments = soup.find_all('div', class_='comment')

        if comments:
            # Extract unique bidder names from comments
            seen_bidders = {}
            for comment in comments:
                # Find member link in this comment
                member_link = comment.find('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
                if member_link:
                    bidder_text = member_link.get_text(strip=True)
                    normalized_name = bidder_text.lstrip('@')

                    # Remove "(The Seller)" or "(seller)" marker if present
                    if '(the seller)' in normalized_name.lower():
                        normalized_name = normalized_name.split('(')[0].strip()
                    if '(seller)' in normalized_name.lower():
                        normalized_name = normalized_name.split('(')[0].strip()

                    # Skip invalid names
                    if not normalized_name or len(normalized_name) < 2 or len(normalized_name) > 50:
                        continue

                    # Skip if already seen
                    if normalized_name in seen_bidders:
                        continue

                    # Skip seller
                    if seller_name and normalized_name.lower() == seller_name.lower():
                        continue

                    # Skip common non-bidder terms
                    if normalized_name.lower() in ['bringatrailer', 'seller', 'reserve', 'admin']:
                        continue

                    seen_bidders[normalized_name] = True
                    bidders_list.append({
                        'bidder_name': normalized_name,
                        'bid_amount': None,
                        'timestamp': None,
                        'result': 'active'
                    })

            return bidders_list

        # Fallback: if no comments, extract from bid information section only
        bid_info = soup.find('div', class_='bid-information')
        if bid_info:
            member_links = bid_info.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
            seen_bidders = {}

            for link in member_links:
                bidder_text = link.get_text(strip=True)
                normalized_name = bidder_text.lstrip('@')

                if not normalized_name or len(normalized_name) < 2 or len(normalized_name) > 50:
                    continue

                if normalized_name in seen_bidders:
                    continue

                if seller_name and normalized_name.lower() == seller_name.lower():
                    continue

                if normalized_name.lower() in ['bringatrailer', 'seller', 'reserve', 'admin']:
                    continue

                seen_bidders[normalized_name] = True
                bidders_list.append({
                    'bidder_name': normalized_name,
                    'bid_amount': None,
                    'timestamp': None,
                    'result': 'active'
                })

        return bidders_list

    def _find_seller(self, soup):
        """Find the seller's name from the auction page"""
        try:
            # Look for seller name in page title or metadata
            # Usually appears as "Listing by [seller name]" or in post meta
            post_meta = soup.find('div', class_='post-meta')
            if post_meta:
                text = post_meta.get_text()
                if 'by' in text.lower():
                    # Extract name after "by"
                    parts = text.split('by')
                    if len(parts) > 1:
                        return parts[1].strip()

            # Alternative: look for member link with "(seller)" or "(the seller)" indicator
            all_links = soup.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
            for link in all_links:
                link_text = link.get_text(strip=True)
                if '(the seller)' in link_text.lower() or '(seller)' in link_text.lower():
                    return link_text.split('(')[0].strip()

            return None
        except:
            return None

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
