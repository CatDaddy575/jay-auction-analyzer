from bs4 import BeautifulSoup
import re

class AuctionScraper:
    """Extract auction data from BringATrailer pages"""

    def parse_auction_page(self, html):
        """Parse HTML and extract auction details"""
        soup = BeautifulSoup(html, 'html.parser')

        auction_data = {
            'title': self._extract_text(soup, 'h1.auction-title'),
            'asking_price': self._parse_price(soup, '.asking-price'),
            'current_bid': self._parse_price(soup, '.current-bid'),
            'bid_count': self._extract_int(soup, '.bid-count'),
            'ends_at': soup.find(attrs={'data-ends-at'}).get('data-ends-at') if soup.find(attrs={'data-ends-at'}) else None,
            'description': self._extract_text(soup, '.description')
        }

        # Extract bidding history
        bidding_history = []
        bid_rows = soup.select('table.bid-history tbody tr')

        for row in bid_rows:
            bid_entry = {
                'bidder': self._extract_text(row, 'td.bidder'),
                'amount': self._parse_price(row, 'td.amount'),
                'timestamp': row.find('td', class_='time').get('data-timestamp') if row.find('td', class_='time') else None
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
