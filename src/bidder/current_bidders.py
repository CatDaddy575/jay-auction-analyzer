"""
Current bidders analyzer - Analyzes competitors on the current auction
Shows win rates and overpayment analysis
"""

from typing import List, Dict
from .profile_scraper import BidderProfileScraper
from .analyzer import BidderBehaviorAnalyzer
import requests
from bs4 import BeautifulSoup
import re


class CurrentBiddersAnalyzer:
    """Analyzes current bidders on an auction to predict competition"""

    def __init__(self):
        self.scraper = BidderProfileScraper()
        self.analyzer = BidderBehaviorAnalyzer()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def analyze_auction_competitors(self, bidder_names: List[str], estimated_market_value: int = 0) -> List[Dict]:
        """
        Analyze all current bidders on an auction

        Args:
            bidder_names: List of bidder usernames on the current auction
            estimated_market_value: Estimated market value for overpayment calculation

        Returns:
            List of competitor analyses sorted by threat level
        """
        competitors = []

        for bidder_name in bidder_names:
            if not bidder_name or bidder_name.strip() == '':
                continue

            analysis = self._analyze_single_competitor(bidder_name, estimated_market_value)
            if analysis:
                competitors.append(analysis)

        # Sort by threat level (high win rate = high threat)
        competitors.sort(key=lambda x: x['threat_level'], reverse=True)

        return competitors

    def _analyze_single_competitor(self, bidder_name: str, market_value: int) -> Dict:
        """Analyze a single competitor"""
        try:
            # Get their profile
            profile = self.scraper.scrape_bidder_profile(bidder_name, use_playwright=False)

            if 'error' in profile:
                return None

            stats = profile['basic_stats']
            total_bids = stats['total_bids']
            total_wins = stats['total_wins']

            # Calculate win rate
            win_rate = (total_wins / total_bids * 100) if total_bids > 0 else 0

            # Analyze their winning auctions for overpayment
            overpayment_analysis = self._analyze_winning_auctions(bidder_name, market_value)

            # Calculate threat level (0-100)
            threat_level = self._calculate_threat_level(win_rate, total_bids, overpayment_analysis)

            # Classify bidder type
            bidder_type = self._classify_bidder_type(win_rate, total_bids, overpayment_analysis)

            return {
                'bidder_name': bidder_name,
                'stats': {
                    'total_bids': total_bids,
                    'total_wins': total_wins,
                    'win_rate': round(win_rate, 1),
                    'member_since': stats['member_since']
                },
                'overpayment_analysis': overpayment_analysis,
                'bidder_type': bidder_type,
                'threat_level': threat_level,
                'recommendation': self._get_recommendation(bidder_type, threat_level, win_rate)
            }

        except Exception as e:
            return None

    def _analyze_winning_auctions(self, bidder_name: str, estimated_market_value: int) -> Dict:
        """
        Analyze bidder's winning auctions to determine if they overpay

        Returns metrics about their win prices vs market value
        """
        analysis = {
            'total_wins': 0,
            'overpaid_count': 0,
            'underpaid_count': 0,
            'avg_overpayment_percent': 0,
            'bidder_discipline': 'unknown'
        }

        # TODO: When we have full bid history, analyze each winning auction
        # For now, return placeholder
        # Future: Visit each winning auction page, extract their bid, compare to market

        return analysis

    def _calculate_threat_level(self, win_rate: float, total_bids: int, overpayment: Dict) -> int:
        """
        Calculate threat level (0-100)
        Higher = more dangerous competitor
        """
        threat = 0

        # Win rate contribution (0-50 points)
        if win_rate > 50:
            threat += 50
        elif win_rate > 25:
            threat += 40
        elif win_rate > 10:
            threat += 25
        elif win_rate > 5:
            threat += 15
        else:
            threat += 5

        # Bid frequency (0-30 points) - more bids = more aggressive
        if total_bids > 100:
            threat += 30
        elif total_bids > 50:
            threat += 20
        elif total_bids > 20:
            threat += 15
        else:
            threat += 5

        # Discipline (0-20 points) - overpaying = will outbid you
        avg_overpay = overpayment.get('avg_overpayment_percent', 0)
        if avg_overpay > 10:
            threat += 20  # Emotional bidder will overpay to win
        elif avg_overpay > 5:
            threat += 10
        else:
            threat += 5

        return min(threat, 100)

    def _classify_bidder_type(self, win_rate: float, total_bids: int, overpayment: Dict) -> str:
        """Classify bidder as Rational, Emotional, or Selective"""
        if total_bids < 10:
            return 'Casual'
        elif win_rate > 40:
            return 'Selective (High Win Rate)'
        elif win_rate < 5 and total_bids > 30:
            return 'Emotional (Bids a lot, wins rarely)'
        else:
            return 'Balanced'

    def _get_recommendation(self, bidder_type: str, threat_level: int, win_rate: float) -> str:
        """Get strategy recommendation for competing with this bidder"""
        if threat_level > 75:
            return 'HIGH THREAT: This bidder is aggressive. Be prepared to bid hard or consider skipping.'
        elif threat_level > 50:
            return 'MEDIUM THREAT: Competitive bidder. Be strategic with your bids.'
        elif win_rate < 3:
            return 'LOW THREAT: Rarely wins. You have a good chance if you bid disciplined.'
        else:
            return 'Monitor their bidding pattern. Set a max and stick to it.'
