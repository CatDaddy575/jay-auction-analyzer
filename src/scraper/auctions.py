from bs4 import BeautifulSoup
import re

class AuctionScraper:
    """Extract auction data from BringATrailer pages"""

    def parse_auction_page(self, html):
        """Parse HTML and extract auction details from BringATrailer"""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title_elem = soup.find('h1', class_='post-title listing-post-title')
        title = title_elem.get_text(strip=True) if title_elem else ''

        # Extract current bid (in format "USD $38,250")
        current_bid = 0
        listing_avail = soup.find('div', class_='listing-available')
        if listing_avail:
            # Look for "Current Bid:" specifically
            bid_label = listing_avail.find('span', class_='info-label', string=lambda s: 'current' in s.lower() if s else False)
            if bid_label:
                # The price is in the next sibling or nearby strong tag
                value_elem = bid_label.find_next('strong', class_='info-value')
                if value_elem:
                    current_bid = self._parse_price(value_elem, None)

        # Extract other info
        auction_data = {
            'title': title,
            'asking_price': 0,  # BringATrailer typically doesn't show asking price on listing page
            'current_bid': current_bid,
            'bid_count': 0,  # Would need to parse bid history to count
            'ends_at': None,  # Would need to parse countdown
            'description': self._extract_text(soup, '.listing-description') or self._extract_text(soup, '.description')
        }

        # Extract bidding history
        bidding_history = []
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

        return {'auction_data': auction_data, 'bidding_history': bidding_history}

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
