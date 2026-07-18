"""
Bidder profile scraper - Extracts bidding history from BringATrailer bidder pages
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class BidderProfileScraper:
    """Scrapes bidder profile pages from BringATrailer"""

    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def scrape_bidder_profile(self, bidder_name, use_playwright=True):
        """
        Fetch and parse a bidder's profile page

        Args:
            bidder_name: Bidder username (e.g., "JSpringer")
            use_playwright: Use Playwright to render JavaScript (default True)

        Returns:
            Dict with bidder stats and history
        """
        url = f"https://bringatrailer.com/member/{bidder_name}/"

        try:
            # Get basic stats from static HTML
            response = requests.get(url, headers=self.headers, timeout=10)
            html_static = response.text
            soup_static = BeautifulSoup(html_static, 'html.parser')

            basic_stats = self._extract_basic_stats(soup_static)

            # Get bid history (requires JavaScript rendering)
            bidding_history = []
            if use_playwright and PLAYWRIGHT_AVAILABLE:
                bidding_history = self._extract_bidding_history_playwright(url)
            else:
                # Fallback to static extraction (usually empty for BringATrailer)
                bidding_history = self._extract_bidding_history_static(soup_static)

            profile_data = {
                'bidder_name': bidder_name,
                'profile_url': url,
                'basic_stats': basic_stats,
                'bidding_history': bidding_history,
                'activity_breakdown': self._analyze_activity_types(soup_static)
            }

            return profile_data

        except Exception as e:
            return {
                'bidder_name': bidder_name,
                'error': str(e),
                'basic_stats': {},
                'bidding_history': [],
                'activity_breakdown': {}
            }

    def _extract_basic_stats(self, soup):
        """Extract basic profile stats (bids placed, wins, etc)"""
        stats = {
            'total_bids': 0,
            'total_wins': 0,
            'total_comments': 0,
            'total_listings': 0,
            'member_since': None,
            'location': None
        }

        # Get all text to find stats
        all_text = soup.get_text()

        # Extract stats from text patterns like "Bids(46)Comments(11)Auction Win(1)"
        bids_match = re.search(r'Bids\s*\((\d+)\)', all_text)
        if bids_match:
            stats['total_bids'] = int(bids_match.group(1))

        wins_match = re.search(r'Auction Win\s*\((\d+)\)', all_text, re.IGNORECASE)
        if wins_match:
            stats['total_wins'] = int(wins_match.group(1))

        comments_match = re.search(r'Comments\s*\((\d+)\)', all_text)
        if comments_match:
            stats['total_comments'] = int(comments_match.group(1))

        listings_match = re.search(r'Listings\s*\((\d+)\)', all_text)
        if listings_match:
            stats['total_listings'] = int(listings_match.group(1))

        # Extract member since date
        member_since_match = re.search(r'Member\s+since\s+(\w+\s+\d{4})', all_text, re.IGNORECASE)
        if member_since_match:
            stats['member_since'] = member_since_match.group(1)

        return stats

    def _extract_bidding_history_static(self, soup):
        """Extract bidding history from static HTML (usually empty for BringATrailer)"""
        history = []

        # Look for bid history table
        bid_table = soup.find('table', class_=lambda x: x and 'bid' in x.lower() if x else False)

        if bid_table:
            rows = bid_table.find_all('tr')[1:]  # Skip header

            for row in rows[:100]:  # Limit to 100 bids
                cells = row.find_all('td')
                if len(cells) >= 4:
                    try:
                        listing_link = cells[0].find('a')
                        listing_name = listing_link.get_text(strip=True) if listing_link else 'Unknown'
                        listing_url = listing_link['href'] if listing_link and listing_link.has_attr('href') else ''

                        bid_amount_text = cells[1].get_text(strip=True)
                        bid_amount = self._parse_price(bid_amount_text)

                        result_text = cells[2].get_text(strip=True).lower()
                        if 'won' in result_text:
                            result = 'won'
                        elif 'lost' in result_text or 'outbid' in result_text:
                            result = 'lost'
                        else:
                            result = 'unknown'

                        date_text = cells[3].get_text(strip=True) if len(cells) > 3 else ''

                        history.append({
                            'listing_name': listing_name,
                            'listing_url': listing_url,
                            'bid_amount': bid_amount,
                            'result': result,
                            'date': date_text
                        })
                    except Exception as e:
                        continue

        return history

    def _extract_bidding_history_playwright(self, url):
        """Extract bidding history using Playwright (renders JavaScript)"""
        if not PLAYWRIGHT_AVAILABLE:
            return []

        history = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_load_state('networkidle', timeout=15000)

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                # Look for bid history table/list in rendered HTML
                bid_table = soup.find('table', class_=lambda x: x and ('bid' in x.lower() or 'history' in x.lower()) if x else False)

                if bid_table:
                    rows = bid_table.find_all('tr')[1:]  # Skip header
                    for row in rows[:100]:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            try:
                                # Extract listing name/link
                                listing_link = cells[0].find('a')
                                listing_name = listing_link.get_text(strip=True) if listing_link else 'Unknown'

                                # Extract bid amount
                                bid_text = cells[1].get_text(strip=True) if len(cells) > 1 else '0'
                                bid_amount = self._parse_price(bid_text)

                                # Determine result (won/lost)
                                result_text = cells[2].get_text(strip=True).lower() if len(cells) > 2 else 'unknown'
                                result = 'won' if 'won' in result_text else 'lost' if 'lost' in result_text or 'outbid' in result_text else 'unknown'

                                if bid_amount > 0:
                                    history.append({
                                        'listing_name': listing_name,
                                        'bid_amount': bid_amount,
                                        'result': result,
                                        'date': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                                    })
                            except Exception as e:
                                continue

                browser.close()

        except Exception as e:
            print(f"Playwright extraction error: {e}")

        return history

    def _analyze_activity_types(self, soup):
        """Analyze bidder's activity breakdown (bids, sales, comments, etc)"""
        activity = {
            'bids_placed': 0,
            'auctions_won': 0,
            'auctions_lost': 0,
            'listings_posted': 0,
            'comments_made': 0
        }

        # Extract from stats
        stats_section = soup.find('div', class_='member-stats')
        if stats_section:
            text = stats_section.get_text()
            # Parse various activity metrics
            if 'bid' in text.lower():
                match = re.search(r'(\d+)\s+bids?', text, re.IGNORECASE)
                if match:
                    activity['bids_placed'] = int(match.group(1))

        return activity

    def _parse_price(self, text):
        """Extract numeric price from text"""
        try:
            match = re.search(r'\$?([\d,]+)', text)
            if match:
                return int(match.group(1).replace(',', ''))
        except:
            pass
        return 0
