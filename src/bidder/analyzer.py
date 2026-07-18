"""
Bidder behavior analyzer - Analyzes patterns and predicts future behavior
"""

from typing import Dict, List
import re


class BidderBehaviorAnalyzer:
    """Analyzes bidder behavior patterns and predicts likely actions"""

    def analyze_profile(self, profile_data: Dict) -> Dict:
        """
        Analyze a bidder's profile and generate behavior insights

        Args:
            profile_data: From BidderProfileScraper.scrape_bidder_profile()

        Returns:
            Dict with comprehensive behavior analysis
        """
        if 'error' in profile_data:
            return {'error': profile_data['error']}

        basic_stats = profile_data['basic_stats']
        history = profile_data['bidding_history']

        # Calculate all metrics
        win_rate = self._calculate_win_rate(history)
        overpayment_analysis = self._analyze_overpayment(history)
        bid_patterns = self._analyze_bid_patterns(history)
        vehicle_segmentation = self._segment_by_vehicle_type(history)
        price_segmentation = self._segment_by_price_range(history)
        motivation = self._infer_motivation(history, win_rate)

        return {
            'bidder': profile_data['bidder_name'],
            'profile_url': profile_data['profile_url'],
            'basic_stats': {
                'total_bids': basic_stats['total_bids'],
                'total_wins': basic_stats['total_wins'],
                'win_rate_overall': win_rate['overall_rate'],
                'member_since': basic_stats['member_since']
            },
            'behavioral': {
                'avg_overpayment_percent': overpayment_analysis['avg_overpayment'],
                'overpayment_range': overpayment_analysis['range'],
                'bid_velocity': bid_patterns['velocity'],
                'bidding_style': bid_patterns['style'],
                'early_vs_late': bid_patterns['timing'],
                'max_historical_bid': bid_patterns['max_bid'],
                'budget_discipline': bid_patterns['discipline']
            },
            'segmentation': {
                'by_vehicle_type': vehicle_segmentation,
                'by_price_range': price_segmentation
            },
            'prediction': {
                'estimated_motivation': motivation['type'],
                'motivation_confidence': motivation['confidence'],
                'likely_max_bid_for_similar': self._estimate_max_bid(history, vehicle_segmentation),
                'bidding_strategy': self._infer_bidding_strategy(bid_patterns, motivation),
                'give_up_threshold': self._analyze_give_up_pattern(history, win_rate)
            },
            'risk_assessment': self._assess_risk(win_rate, overpayment_analysis, motivation)
        }

    def _calculate_win_rate(self, history: List[Dict]) -> Dict:
        """Calculate overall and segmented win rates"""
        if not history:
            return {'overall_rate': 0, 'by_segment': {}}

        total = len(history)
        wins = sum(1 for bid in history if bid['result'] == 'won')
        losses = sum(1 for bid in history if bid['result'] == 'lost')

        return {
            'overall_rate': round((wins / total * 100), 1) if total > 0 else 0,
            'total_bids': total,
            'total_wins': wins,
            'total_losses': losses,
            'win_loss_ratio': f"{wins}:{losses}"
        }

    def _analyze_overpayment(self, history: List[Dict]) -> Dict:
        """
        Analyze how much bidder overpays relative to market value
        TODO: Implement market value comparison when market data sources are available
        """
        # For now, return placeholder structure
        # When market data is available, compare bid amounts to estimated market values
        return {
            'avg_overpayment': 0,  # Will be calculated from market data
            'range': {'min': 0, 'max': 0},
            'note': 'Requires market value data source implementation'
        }

    def _analyze_bid_patterns(self, history: List[Dict]) -> Dict:
        """Analyze bidding patterns (velocity, style, timing, discipline)"""
        if not history:
            return {
                'velocity': 'unknown',
                'style': 'unknown',
                'timing': 'unknown',
                'max_bid': 0,
                'discipline': 'unknown'
            }

        # Calculate bid statistics
        bids = [b['bid_amount'] for b in history if b['bid_amount'] > 0]
        max_bid = max(bids) if bids else 0
        avg_bid = sum(bids) / len(bids) if bids else 0

        # Infer patterns
        velocity = self._infer_velocity(bids)
        style = self._infer_style(bids)
        discipline = self._infer_discipline(bids, history)

        # Timing (early vs late bidder)
        # TODO: Parse bid timestamps when available
        timing = 'unknown'

        return {
            'velocity': velocity,
            'style': style,
            'timing': timing,
            'max_bid': max_bid,
            'avg_bid': round(avg_bid),
            'bid_range': f"${min(bids):,} - ${max_bid:,}" if bids else "unknown",
            'discipline': discipline
        }

    def _segment_by_vehicle_type(self, history: List[Dict]) -> Dict:
        """Segment bidding history by vehicle type"""
        segments = {}

        for bid in history:
            listing_name = bid['listing_name'].lower()

            # Infer vehicle type from listing name
            vehicle_type = self._infer_vehicle_type(listing_name)

            if vehicle_type not in segments:
                segments[vehicle_type] = {'bids': 0, 'wins': 0, 'avg_bid': 0}

            segments[vehicle_type]['bids'] += 1
            if bid['result'] == 'won':
                segments[vehicle_type]['wins'] += 1
            segments[vehicle_type]['avg_bid'] = bid['bid_amount']

        # Calculate win rates per segment
        for vehicle_type in segments:
            bids = segments[vehicle_type]['bids']
            wins = segments[vehicle_type]['wins']
            segments[vehicle_type]['win_rate'] = round((wins / bids * 100), 1) if bids > 0 else 0

        return segments

    def _segment_by_price_range(self, history: List[Dict]) -> Dict:
        """Segment bidding history by price range"""
        segments = {
            'under_20k': {'bids': 0, 'wins': 0},
            '20k_50k': {'bids': 0, 'wins': 0},
            '50k_100k': {'bids': 0, 'wins': 0},
            'over_100k': {'bids': 0, 'wins': 0}
        }

        for bid in history:
            amount = bid['bid_amount']

            if amount < 20000:
                key = 'under_20k'
            elif amount < 50000:
                key = '20k_50k'
            elif amount < 100000:
                key = '50k_100k'
            else:
                key = 'over_100k'

            segments[key]['bids'] += 1
            if bid['result'] == 'won':
                segments[key]['wins'] += 1

        # Calculate win rates
        for key in segments:
            bids = segments[key]['bids']
            wins = segments[key]['wins']
            segments[key]['win_rate'] = round((wins / bids * 100), 1) if bids > 0 else 0

        return segments

    def _infer_motivation(self, history: List[Dict], win_rate: Dict) -> Dict:
        """Infer bidder's motivation (collector vs dealer vs casual)"""
        if not history:
            return {'type': 'unknown', 'confidence': 0}

        total_bids = len(history)
        wins = win_rate['total_wins']
        win_rate_pct = win_rate['overall_rate']

        # Heuristics for motivation type
        if win_rate_pct > 60:
            # High win rate suggests:
            # - Only bids on cars they're confident about
            # - Disciplined, possibly dealer/flipper
            motivation_type = 'dealer_or_disciplined_collector'
            confidence = 75
        elif win_rate_pct < 20:
            # Low win rate suggests:
            # - Bids a lot, wins rarely
            # - Could be casual/emotional bidder
            # - Gets outbid often
            motivation_type = 'casual_or_emotional_bidder'
            confidence = 70
        else:
            # Medium win rate
            motivation_type = 'mixed_pattern'
            confidence = 60

        return {
            'type': motivation_type,
            'confidence': confidence,
            'reasoning': f"Win rate {win_rate_pct}% on {total_bids} bids"
        }

    def _infer_velocity(self, bids: List[int]) -> str:
        """Infer bid velocity (fast/slow/reactive)"""
        if not bids:
            return 'unknown'

        avg_bid = sum(bids) / len(bids)
        max_bid = max(bids)

        if max_bid > avg_bid * 2:
            return 'reactive (big jumps)'
        elif max_bid <= avg_bid * 1.1:
            return 'steady (consistent increments)'
        else:
            return 'moderate (variable increments)'

    def _infer_style(self, bids: List[int]) -> str:
        """Infer bidding style (aggressive/conservative/balanced)"""
        if not bids or len(bids) < 3:
            return 'unknown'

        # Look at bid increments
        increments = [bids[i+1] - bids[i] for i in range(len(bids)-1) if bids[i+1] > bids[i]]

        if increments:
            avg_increment_pct = (sum(increments) / sum(bids[:-1]) * 100) / len(increments)

            if avg_increment_pct > 5:
                return 'aggressive (large increments)'
            elif avg_increment_pct < 1:
                return 'conservative (small increments)'
            else:
                return 'balanced'
        return 'unknown'

    def _infer_discipline(self, bids: List[int], history: List[Dict]) -> str:
        """Infer budget discipline (disciplined/emotional/unknown)"""
        wins = sum(1 for b in history if b['result'] == 'won')

        if not wins:
            return 'unknown'

        # If they win at high bids but lose more often, they might lack discipline
        winning_bids = [h['bid_amount'] for h in history if h['result'] == 'won' and h['bid_amount'] > 0]

        if winning_bids and max(winning_bids) > 50000:
            return 'high_spending (willing to pay big)'
        elif not winning_bids:
            return 'unknown'
        else:
            return 'disciplined (conservative bids)'

    def _infer_vehicle_type(self, listing_name: str) -> str:
        """Infer vehicle type from listing name"""
        if 'truck' in listing_name:
            return 'trucks'
        elif 'ford' in listing_name or 'chevy' in listing_name or 'dodge' in listing_name:
            return 'american_classics'
        elif 'porsche' in listing_name or 'ferrari' in listing_name or 'lamborghini' in listing_name:
            return 'exotic'
        elif 'motorcycle' in listing_name:
            return 'motorcycles'
        else:
            return 'other'

    def _estimate_max_bid(self, history: List[Dict], vehicle_segments: Dict) -> Dict:
        """Estimate likely max bid for similar auctions"""
        max_bids = [h['bid_amount'] for h in history if h['bid_amount'] > 0]

        if not max_bids:
            return {'estimate': 0, 'confidence': 0}

        return {
            'historical_max': max(max_bids),
            'historical_avg': round(sum(max_bids) / len(max_bids)),
            'percentile_95': sorted(max_bids)[int(len(max_bids) * 0.95)] if len(max_bids) > 10 else max(max_bids),
            'note': 'Adjust for current market conditions and vehicle specifics'
        }

    def _infer_bidding_strategy(self, bid_patterns: Dict, motivation: Dict) -> str:
        """Infer likely bidding strategy"""
        style = bid_patterns['style']
        motivation_type = motivation['type']

        if 'dealer' in motivation_type:
            return 'Rational: Sets max bid, sticks to it, won\'t overpay'
        elif 'casual' in motivation_type:
            return 'Emotional: Bids impulsively, might give up if pushed hard'
        elif 'aggressive' in style:
            return 'Aggressive: Large bid jumps, likely trying to intimidate competitors'
        else:
            return 'Balanced: Steady, incremental bidding'

    def _analyze_give_up_pattern(self, history: List[Dict], win_rate: Dict) -> Dict:
        """Analyze at what point bidders typically give up"""
        losses = [b for b in history if b['result'] == 'lost']

        if not losses:
            return {'threshold': 'unknown', 'note': 'Bidder rarely gives up'}

        loss_amounts = [b['bid_amount'] for b in losses if b['bid_amount'] > 0]

        if loss_amounts:
            avg_loss_amount = sum(loss_amounts) / len(loss_amounts)
            return {
                'avg_final_bid_before_loss': round(avg_loss_amount),
                'note': 'On average, loses when outbid at this amount'
            }

        return {'threshold': 'unknown', 'note': 'Insufficient data'}

    def _assess_risk(self, win_rate: Dict, overpayment: Dict, motivation: Dict) -> Dict:
        """Comprehensive risk assessment"""
        wins = win_rate.get('total_wins', 0)
        total = win_rate.get('total_bids', 1)
        win_pct = win_rate.get('overall_rate', 0)

        if win_pct > 70:
            risk_level = 'HIGH'
            reason = 'High win rate—strong competitor, willing to pay'
        elif win_pct < 15:
            risk_level = 'LOW'
            reason = 'Low win rate—gives up easily or plays safe'
        else:
            risk_level = 'MEDIUM'
            reason = 'Moderate competition—balanced approach'

        return {
            'level': risk_level,
            'reason': reason,
            'competitive_strength': 'strong' if wins > 20 else 'weak' if wins < 5 else 'moderate',
            'recommendation': f'This bidder is {risk_level} risk. {reason}'
        }
