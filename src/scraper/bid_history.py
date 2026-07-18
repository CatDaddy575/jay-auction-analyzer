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
        Tries Playwright if available, otherwise uses static HTML.
        Returns list of dicts: {bidder_name, bid_amount, timestamp, result}
        """
        # Try Playwright first (better extraction)
        try:
            from playwright.sync_api import sync_playwright
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(auction_url, wait_until='domcontentloaded', timeout=30000)

            try:
                page.wait_for_load_state('load', timeout=5000)
            except:
                pass

            html = page.content()
            page.close()
            browser.close()
            playwright.stop()

            return self._parse_bid_history(html, auction_url)

        except ImportError:
            print("Playwright not available, using static HTML...")
            # Fallback to static HTML scraping
            try:
                import requests
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(auction_url, headers=headers, timeout=10)
                return self._parse_bid_history(response.text, auction_url)
            except Exception as fallback_error:
                print(f"Static HTML fallback failed: {fallback_error}")
                return []
        except Exception as e:
            print(f"Playwright error ({e}), falling back to static HTML...")
            try:
                import requests
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(auction_url, headers=headers, timeout=10)
                return self._parse_bid_history(response.text, auction_url)
            except Exception as fallback_error:
                print(f"Static HTML fallback also failed: {fallback_error}")
                return []

    def _parse_bid_history(self, html, auction_url):
        """Parse bid history - track highest bid, bid count, and timestamps per bidder"""
        soup = BeautifulSoup(html, 'html.parser')
        bidders_data = {}  # {bidder_name: {'highest_bid': X, 'bid_count': Y, 'latest_bid': X, 'latest_time': T, 'bids': [...]}}

        # First, find the seller so we can exclude them
        seller_name = self._find_seller(soup)

        # PRIORITY 1: Extract current high bid from bid-information section
        current_high_bidder, current_high_amount = self._find_current_high_bid(soup)
        if current_high_bidder and current_high_bidder.lower() != seller_name.lower() if seller_name else True:
            if current_high_bidder not in bidders_data:
                bidders_data[current_high_bidder] = {'highest_bid': 0, 'latest_bid': 0, 'latest_time': None, 'bid_count': 0, 'bids': []}
            if current_high_amount > bidders_data[current_high_bidder]['highest_bid']:
                bidders_data[current_high_bidder]['highest_bid'] = current_high_amount
            bidders_data[current_high_bidder]['latest_bid'] = current_high_amount
            bidders_data[current_high_bidder]['bids'].append({'amount': current_high_amount, 'time': None})
            bidders_data[current_high_bidder]['bid_count'] += 1

        # Extract all bids from comments section
        comments = soup.find_all('div', class_='comment')

        if comments:
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

                    # Skip seller
                    if seller_name and normalized_name.lower() == seller_name.lower():
                        continue

                    # Skip common non-bidder terms
                    if normalized_name.lower() in ['bringatrailer', 'seller', 'reserve', 'admin']:
                        continue

                    # Extract bid amount and timestamp from comment
                    bid_amount = self._extract_bid_amount(comment)
                    bid_time = self._extract_bid_timestamp(comment)

                    # Initialize bidder if not seen
                    if normalized_name not in bidders_data:
                        bidders_data[normalized_name] = {'highest_bid': 0, 'latest_bid': 0, 'latest_time': None, 'bid_count': 0, 'bids': []}

                    # Track this bid
                    if bid_amount > 0:
                        bidders_data[normalized_name]['bids'].append({'amount': bid_amount, 'time': bid_time})
                        bidders_data[normalized_name]['bid_count'] += 1
                        if bid_amount > bidders_data[normalized_name]['highest_bid']:
                            bidders_data[normalized_name]['highest_bid'] = bid_amount
                        # Update latest bid (most recent based on comment order - later comments are more recent)
                        bidders_data[normalized_name]['latest_bid'] = bid_amount
                        bidders_data[normalized_name]['latest_time'] = bid_time

        # Convert to list, sort by highest bid amount (highest first)
        bidders_list = []
        for name in sorted(bidders_data.keys(),
                          key=lambda x: bidders_data[x]['highest_bid'],
                          reverse=True):
            data = bidders_data[name]
            bidders_list.append({
                'bidder_name': name,
                'bid_amount': data['highest_bid'],           # Highest bid placed
                'latest_bid': data['latest_bid'],           # Most recent bid
                'bid_count': data['bid_count'],             # Total bids on this auction
                'latest_time': data['latest_time'],         # Timestamp of latest bid
                'all_bids': data['bids'],                   # All bids with timestamps
                'result': 'active'
            })

        return bidders_list

        # Fallback: if no comments, extract from bid information section only
        if not bidders_dict:
            bid_info = soup.find('div', class_='bid-information')
            if bid_info:
                member_links = bid_info.find_all('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))

                for link in member_links:
                    bidder_text = link.get_text(strip=True)
                    normalized_name = bidder_text.lstrip('@')

                    if not normalized_name or len(normalized_name) < 2 or len(normalized_name) > 50:
                        continue

                    if seller_name and normalized_name.lower() == seller_name.lower():
                        continue

                    if normalized_name.lower() in ['bringatrailer', 'seller', 'reserve', 'admin']:
                        continue

                    if normalized_name not in bidders_dict:
                        bidders_dict[normalized_name] = 0

        # Convert to list and sort by bid amount (highest first)
        bidders_list = []
        for name, amount in sorted(bidders_dict.items(), key=lambda x: x[1] if x[1] else 0, reverse=True):
            bidders_list.append({
                'bidder_name': name,
                'bid_amount': amount,
                'timestamp': None,
                'result': 'active'
            })

        return bidders_list

    def _find_current_high_bid(self, soup):
        """Extract the current high bidder and bid amount from bid-information section"""
        try:
            bid_info = soup.find('div', class_='bid-information')
            if not bid_info:
                return None, None

            # Look for the bidder link in bid information
            member_link = bid_info.find('a', href=lambda x: x and '/member/' in (x if isinstance(x, str) else ''))
            if member_link:
                bidder_name = member_link.get_text(strip=True).lstrip('@')
                # Clean up seller marker if present
                if '(the seller)' in bidder_name.lower():
                    bidder_name = bidder_name.split('(')[0].strip()
                if '(seller)' in bidder_name.lower():
                    bidder_name = bidder_name.split('(')[0].strip()

                # Extract bid amount from bid info section
                bid_text = bid_info.get_text()
                bid_amount = self._extract_bid_amount_from_text(bid_text)

                return bidder_name if bidder_name else None, bid_amount

            return None, None
        except:
            return None, None

    def _extract_bid_amount(self, element):
        """Extract bid amount from a comment or bid element"""
        return self._extract_bid_amount_from_text(element.get_text())

    def _extract_bid_amount_from_text(self, text):
        """Parse bid amount from text like 'USD $50,000 bid placed by' """
        try:
            import re
            # Look for USD $X,XXX or just $X,XXX
            match = re.search(r'\$[\d,]+(?:\.\d{2})?', text)
            if match:
                bid_str = match.group(0).replace('$', '').replace(',', '').strip()
                if bid_str:
                    return float(bid_str)
        except:
            pass
        return 0

    def _extract_bid_timestamp(self, element):
        """Extract bid timestamp from comment (e.g., 'Jul 18 at 6:30 PM')"""
        try:
            import re
            text = element.get_text()
            # Look for timestamp patterns like "Jul 18 at 6:30 PM"
            match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+at\s+\d{1,2}:\d{2}\s+(AM|PM)', text)
            if match:
                return match.group(0)
        except:
            pass
        return None

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
        Get top N active bidders from auction, filtered by actual bid amounts.
        Returns bidders ranked by highest bid (descending).
        Filters out bidders with $0 bids.
        Returns up to 'limit' bidders, or fewer if fewer than 'limit' actually bid.
        """
        all_bids = self.scrape_bid_history(auction_url)

        if not all_bids:
            return []

        # Filter out bidders with no bids ($0 or None)
        bidders_with_bids = [b for b in all_bids if b.get('bid_amount', 0) > 0]

        if not bidders_with_bids:
            return []

        # Return top N (or fewer if less than N bidders)
        return bidders_with_bids[:limit]

    def cleanup(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
