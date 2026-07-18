class StrategyEngine:
    """Strategy recommendation engine"""

    def __init__(self, database):
        self.db = database

    def analyze_auction(self, auction_id):
        """Analyze auction and recommend strategy"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get auction data
        cursor.execute('SELECT * FROM auctions WHERE ba_id = ?', (auction_id,))
        auction = cursor.fetchone()

        if not auction:
            return None

        # Get market data
        cursor.execute(
            'SELECT * FROM market_data WHERE make = ? AND model = ? AND year = ?',
            (auction[3], auction[4], auction[5])  # make, model, year
        )
        market_data = cursor.fetchone()

        # Get bidder history
        cursor.execute(
            'SELECT bidder_username FROM bidding_history WHERE auction_id = ?',
            (auction_id,)
        )
        bidders = cursor.fetchall()

        conn.close()

        analysis = {
            'auction_id': auction_id,
            'fair_market_value': market_data[3] if market_data else None,  # avg_selling_price
            'current_over_under': self._calculate_premium(auction[7], market_data[3]) if market_data else None,
            'competitor_presence': len(set(b[0] for b in bidders)),
            'recommendation': self._generate_recommendation(auction, market_data, bidders),
            'risk_level': self._calculate_risk(auction, bidders)
        }

        return analysis

    def _calculate_premium(self, current_bid, fair_value):
        """Calculate how much over/under fair value"""
        if not fair_value:
            return None
        return round((current_bid - fair_value) / fair_value * 100, 1)

    def _generate_recommendation(self, auction, market_data, bidders):
        """Generate bid recommendation"""
        if not market_data:
            return {'action': 'ANALYZE', 'reason': 'Insufficient market data'}

        fair_value = market_data[3]  # avg_selling_price
        premium = self._calculate_premium(auction[7], fair_value)
        competitor_count = len(set(b[0] for b in bidders))

        if premium > 20:
            return {
                'action': 'SKIP',
                'reason': f'Auction is {premium}% over fair market value'
            }

        if competitor_count > 5:
            return {
                'action': 'AVOID',
                'reason': 'Too much competition'
            }

        return {
            'action': 'MONITOR',
            'reason': 'Reasonable price and competition level'
        }

    def _calculate_risk(self, auction, bidders):
        """Calculate risk level"""
        # Simple risk calculation
        competitor_count = len(set(b[0] for b in bidders))

        if competitor_count > 10:
            return 'HIGH'
        elif competitor_count > 5:
            return 'MEDIUM'
        else:
            return 'LOW'
