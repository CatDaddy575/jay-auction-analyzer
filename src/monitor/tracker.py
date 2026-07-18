from datetime import datetime

class AuctionMonitor:
    """Real-time auction monitoring"""

    def __init__(self, database):
        self.db = database
        self.watchlist = []
        self.alerts = []

    def add_to_watchlist(self, auction_id, options=None):
        """Add auction to watch list"""
        options = options or {}

        self.watchlist.append({
            'auction_id': auction_id,
            'target_price': options.get('target_price'),
            'max_bid': options.get('max_bid'),
            'tracked_bidders': options.get('tracked_bidders', []),
            'added_at': datetime.now()
        })
        print(f'📍 Added auction {auction_id} to watchlist')

    def check_auction(self, auction_id, current_data):
        """Check for changes in auction"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get previous data
        cursor.execute('SELECT current_bid, bid_count FROM auctions WHERE ba_id = ?', (auction_id,))
        result = cursor.fetchone()

        if result:
            previous_bid, previous_count = result

            # Detect price movement
            if current_data['current_bid'] > previous_bid:
                self.alerts.append({
                    'type': 'PRICE_INCREASE',
                    'auction_id': auction_id,
                    'old_bid': previous_bid,
                    'new_bid': current_data['current_bid'],
                    'increase': current_data['current_bid'] - previous_bid
                })

            # Detect new bids
            if current_data['bid_count'] > previous_count:
                self.alerts.append({
                    'type': 'NEW_BID',
                    'auction_id': auction_id,
                    'bid_count': current_data['bid_count']
                })

        conn.close()

    def get_alerts(self):
        """Get all alerts"""
        return self.alerts

    def clear_alerts(self):
        """Clear alerts"""
        self.alerts = []
