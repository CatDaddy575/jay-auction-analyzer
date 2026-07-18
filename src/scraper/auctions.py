from bs4 import BeautifulSoup
import re

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class AuctionScraper:
    """Extract auction data from BringATrailer pages"""

    def parse_auction_page(self, html, url=None):
        """
        Parse HTML and extract auction details from BringATrailer
        Tries static HTML first, falls back to Playwright if bid history not found
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title_elem = soup.find('h1', class_='post-title listing-post-title')
        title = title_elem.get_text(strip=True) if title_elem else ''

        # Extract current bid
        current_bid = 0
        listing_avail = soup.find('div', class_='listing-available')
        if listing_avail:
            bid_label = listing_avail.find('span', class_='info-label', string=lambda s: 'current' in s.lower() if s else False)
            if bid_label:
                value_elem = bid_label.find_next('strong', class_='info-value')
                if value_elem:
                    current_bid = self._parse_price(value_elem, None)

        # Try to extract bid count from the table
        bid_count = 0
        bid_count_elem = soup.find('td', class_='number-bids-value')
        if bid_count_elem:
            bid_count = self._extract_int(bid_count_elem, '')

        auction_data = {
            'title': title,
            'asking_price': 0,
            'current_bid': current_bid,
            'bid_count': bid_count,
            'ends_at': None,
            'description': self._extract_text(soup, '.listing-description') or self._extract_text(soup, '.description')
        }

        # Try to extract bidding history from static HTML first
        bidding_history = self._extract_bidding_history_static(soup)

        # If no bids found and URL provided, try Playwright as fallback
        if not bidding_history and url and PLAYWRIGHT_AVAILABLE:
            try:
                bidding_history = self._extract_bidding_history_playwright(url)
            except Exception as e:
                print(f"Playwright extraction failed: {e}")

        return {'auction_data': auction_data, 'bidding_history': bidding_history}

    def _extract_bidding_history_static(self, soup):
        """Extract bidding history from static HTML (fast, always works)"""
        bidding_history = []

        # Try multiple possible selectors for bid history
        bid_history_section = soup.find('div', class_='bid-history-container')

        if bid_history_section:
            bid_rows = bid_history_section.find_all('li', class_='bid-history-item')
            for row in bid_rows:
                bidder_elem = row.find(class_='bid-history-bidder')
                amount_elem = row.find(class_='bid-history-amount')
                time_elem = row.find(class_='bid-history-time')

                if bidder_elem and amount_elem:
                    bid_entry = {
                        'bidder': bidder_elem.get_text(strip=True),
                        'amount': self._parse_price(amount_elem, None),
                        'timestamp': time_elem.get_text(strip=True) if time_elem else None
                    }
                    bidding_history.append(bid_entry)

        return bidding_history

    def _extract_bidding_history_playwright(self, url):
        """Extract bidding history using Playwright (slower, handles JavaScript)"""
        if not PLAYWRIGHT_AVAILABLE:
            return []

        bidding_history = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle')

                # Wait for bid history to load
                page.wait_for_selector('[class*="bid"]', timeout=5000)

                # Get the rendered HTML and parse with BeautifulSoup
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                # Try to find bid entries in the rendered page
                bid_entries = soup.find_all('div', class_=lambda x: x and 'bid' in x.lower())

                # Parse each bid entry (selector may vary)
                for entry in bid_entries[:50]:  # Limit to 50 bids
                    bidder = entry.find(class_=lambda x: x and 'bidder' in x.lower())
                    amount = entry.find(class_=lambda x: x and 'amount' in x.lower())

                    if bidder and amount:
                        bidding_history.append({
                            'bidder': bidder.get_text(strip=True),
                            'amount': self._parse_price(amount, None),
                            'timestamp': None
                        })

                browser.close()
        except Exception as e:
            print(f"Playwright error: {e}")

        return bidding_history

    def _extract_text(self, element, selector):
        """Safely extract text from element"""
        try:
            el = element.select_one(selector)
            return el.get_text(strip=True) if el else ''
        except:
            return ''

    def _parse_price(self, element, selector):
        """Extract and parse price from text"""
        try:
            if selector is None:
                # Element passed directly
                text = element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
            else:
                text = self._extract_text(element, selector)

            match = re.search(r'\$?([\d,]+)', text)
            return int(match.group(1).replace(',', '')) if match else 0
        except:
            return 0

    def _extract_int(self, element, selector):
        """Extract integer from text"""
        try:
            text = self._extract_text(element, selector)
            match = re.search(r'(\d+)', text)
            return int(match.group(1)) if match else 0
        except:
            return 0

    def extract_competitors(self, bidding_history):
        """Get list of unique bidders from auction"""
        return list(set(bid['bidder'] for bid in bidding_history if bid['bidder']))
