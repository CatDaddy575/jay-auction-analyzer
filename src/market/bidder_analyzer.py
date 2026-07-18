"""
Bidder analyzer - Identifies aggressive bidders and competitive risk
"""

from typing import List, Dict

class BidderAnalyzer:
    """Analyzes bidding patterns to identify heavy hitters and competitive risk"""

    # Known aggressive bidder patterns
    HEAVY_HITTER_THRESHOLD = 0.70  # 70% win rate = heavy hitter

    def __init__(self):
        self.bidders = {}

    def analyze_bidding_history(self, bidding_history: List[Dict]) -> Dict:
        """
        Analyze bidding history to identify patterns

        Args:
            bidding_history: List of bids with bidder, amount, time

        Returns:
            Dict with bidder analysis and risk assessment
        """
        if not bidding_history:
            return {
                'bidders': [],
                'heavy_hitters': [],
                'competitive_risk': 'UNKNOWN',
                'recommendation': 'Insufficient bidding data'
            }

        # Count bids per bidder
        bidder_stats = {}

        for bid in bidding_history:
            bidder = bid.get('bidder', 'Unknown')

            if bidder not in bidder_stats:
                bidder_stats[bidder] = {
                    'bidder': bidder,
                    'bid_count': 0,
                    'total_bids': 0,
                    'max_bid': 0,
                    'min_bid': float('inf')
                }

            bidder_stats[bidder]['bid_count'] += 1
            bidder_stats[bidder]['total_bids'] += bid.get('amount', 0)
            bidder_stats[bidder]['max_bid'] = max(
                bidder_stats[bidder]['max_bid'],
                bid.get('amount', 0)
            )
            bidder_stats[bidder]['min_bid'] = min(
                bidder_stats[bidder]['min_bid'],
                bid.get('amount', 0)
            )

        # Calculate bidder metrics
        for bidder, stats in bidder_stats.items():
            stats['avg_bid'] = (
                stats['total_bids'] / stats['bid_count']
                if stats['bid_count'] > 0 else 0
            )

        # Calculate bidder statistics for all bidders
        all_bidder_stats = []
        total_bids = len(bidding_history)

        for bidder, stats in bidder_stats.items():
            bid_percentage = stats['bid_count'] / total_bids if total_bids > 0 else 0

            all_bidder_stats.append({
                'bidder': bidder,
                'bid_count': stats['bid_count'],
                'bid_percentage': round(bid_percentage * 100, 1),
                'max_bid': stats['max_bid'],
                'avg_bid': round(stats['avg_bid']),
                'risk_level': self._assess_bidder_risk(bid_percentage)
            })

        # Sort by bid count (most active first)
        all_bidder_stats.sort(key=lambda x: x['bid_count'], reverse=True)

        # Identify heavy hitters (bidders with many bids)
        heavy_hitters = [b for b in all_bidder_stats if b['bid_percentage'] >= 15]

        # Assess overall competitive risk
        risk_level = self._assess_overall_risk(len(bidding_history), len(heavy_hitters))

        return {
            'total_bids': total_bids,
            'unique_bidders': len(bidder_stats),
            'all_bidders': all_bidder_stats,
            'heavy_hitters': heavy_hitters,
            'competitive_risk': risk_level,
            'recommendation': self._get_recommendation(risk_level, heavy_hitters)
        }

    def _assess_bidder_risk(self, bid_percentage: float) -> str:
        """Assess individual bidder risk level"""
        if bid_percentage > 0.25:
            return "🔴 HIGH"
        elif bid_percentage > 0.20:
            return "🟠 MEDIUM-HIGH"
        elif bid_percentage > 0.15:
            return "🟠 MEDIUM"
        else:
            return "🟡 LOW"

    def _assess_overall_risk(self, total_bids: int, heavy_hitter_count: int) -> str:
        """Assess overall auction competitive risk"""
        if total_bids < 5:
            return "LOW"
        elif total_bids < 15:
            if heavy_hitter_count >= 2:
                return "MEDIUM"
            return "MEDIUM-LOW"
        elif total_bids < 30:
            if heavy_hitter_count >= 3:
                return "HIGH"
            return "MEDIUM"
        else:
            return "VERY_HIGH"

    def _get_recommendation(self, risk_level: str, heavy_hitters: List[Dict]) -> str:
        """Get bidding recommendation based on competition"""
        if risk_level == "LOW":
            return "✅ Good opportunity - Low competition expected"
        elif risk_level == "MEDIUM-LOW":
            return "⚠️ Light competition - Monitor closely"
        elif risk_level == "MEDIUM":
            return "⚠️ Moderate competition - Strategic bidding recommended"
        elif risk_level == "HIGH":
            if heavy_hitters:
                return f"🚨 HEAVY COMPETITION - {heavy_hitters[0]['bidder']} is aggressive. Careful bidding needed."
            return "🚨 Heavy competition expected - Consider skipping"
        else:
            return "🚨 VERY COMPETITIVE - Multiple aggressive bidders. High risk of overpaying."

    def identify_shill_bidding(self, bidding_history: List[Dict]) -> Dict:
        """
        Attempt to identify potential shill bidding patterns

        Shill bidding patterns:
        - Rapid bids at round increments
        - Same bidder always incrementing slightly
        - Late withdrawal
        """
        # TODO: Implement shill detection
        return {
            'suspected': False,
            'patterns': []
        }
