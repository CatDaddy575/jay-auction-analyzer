"""
BringATrailer fee calculator
Accurately calculates buyer's fees and total cost
"""

class FeeCalculator:
    """Calculate BringATrailer buyer's fees"""

    # BringATrailer fee structure (as of 2026)
    # Tiered buyer's fee with maximum cap:
    # - 8% on bids up to $100,000
    # - 5% on bids above $100,000
    # - Maximum total fee: $7,500 (verify this cap amount)
    # (Verify structure at: https://bringatrailer.com/help/buying/)

    TIER_1_LIMIT = 100_000      # Bids up to $100k
    TIER_1_RATE = 0.08          # 8% fee
    TIER_2_RATE = 0.05          # 5% fee above $100k
    MAX_FEE_CAP = 7_500         # Maximum total fee (TO BE VERIFIED)

    @staticmethod
    def calculate_total_cost(winning_bid: int) -> dict:
        """
        Calculate total cost including tiered buyer's fee (with maximum cap)

        Args:
            winning_bid: The hammer price (winning bid amount)

        Returns:
            Dict with breakdown of costs
        """
        if winning_bid <= FeeCalculator.TIER_1_LIMIT:
            buyer_fee = int(winning_bid * FeeCalculator.TIER_1_RATE)
            fee_rate = FeeCalculator.TIER_1_RATE * 100
        else:
            tier_1_fee = int(FeeCalculator.TIER_1_LIMIT * FeeCalculator.TIER_1_RATE)
            tier_2_amount = winning_bid - FeeCalculator.TIER_1_LIMIT
            tier_2_fee = int(tier_2_amount * FeeCalculator.TIER_2_RATE)
            buyer_fee = tier_1_fee + tier_2_fee
            fee_rate = (buyer_fee / winning_bid * 100) if winning_bid > 0 else 0

        # Apply maximum fee cap if buyer_fee exceeds it
        if buyer_fee > FeeCalculator.MAX_FEE_CAP:
            buyer_fee = FeeCalculator.MAX_FEE_CAP
            fee_rate = (buyer_fee / winning_bid * 100) if winning_bid > 0 else 0

        total_cost = winning_bid + buyer_fee

        return {
            'winning_bid': winning_bid,
            'buyer_fee': buyer_fee,
            'buyer_fee_percent': fee_rate,
            'total_cost': total_cost,
            'fee_per_dollar': round(fee_rate, 2),
            'fee_capped': buyer_fee == FeeCalculator.MAX_FEE_CAP
        }

    @staticmethod
    def calculate_max_bid(target_price: int) -> dict:
        """
        Calculate max bid to stay within target price (including tiered fees with cap)

        If you want to pay max $35,000 total, what's your max bid?

        Args:
            target_price: Maximum total amount willing to pay

        Returns:
            Dict with max bid and resulting total cost
        """
        max_bid = target_price
        cost_calc = None

        for _ in range(100):
            cost_calc = FeeCalculator.calculate_total_cost(max_bid)
            if cost_calc['total_cost'] <= target_price:
                break
            max_bid -= 50

        resulting_calc = FeeCalculator.calculate_total_cost(max_bid)

        return {
            'target_price': target_price,
            'max_bid': max_bid,
            'resulting_total_cost': resulting_calc['total_cost'],
            'fee_amount': resulting_calc['buyer_fee'],
            'fee_capped': resulting_calc['fee_capped'],
            'note': f'Bid up to ${max_bid:,} to stay within ${target_price:,} total'
        }

    @staticmethod
    def get_fee_breakdown(winning_bid: int) -> str:
        """Get human-readable fee breakdown"""
        calc = FeeCalculator.calculate_total_cost(winning_bid)
        return f"""
        Winning Bid:  ${calc['winning_bid']:,}
        Buyer Fee (8%): ${calc['buyer_fee']:,}
        ─────────────
        Total Cost:   ${calc['total_cost']:,}
        """

    @staticmethod
    def reverse_calculate_bid(total_budget: int) -> int:
        """
        Reverse calculate: what's my max bid given a total budget?
        """
        return FeeCalculator.calculate_max_bid(total_budget)['max_bid']
