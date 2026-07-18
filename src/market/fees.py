"""
BringATrailer fee calculator
Accurately calculates buyer's fees and total cost
"""

class FeeCalculator:
    """Calculate BringATrailer buyer's fees"""

    # BringATrailer fee structure (as of 2026)
    # Standard buyer's fee: 8%
    # (Verify this at: https://bringatrailer.com/help/buying/)

    BUYER_FEE_PERCENT = 0.08  # 8%

    @staticmethod
    def calculate_total_cost(winning_bid: int) -> dict:
        """
        Calculate total cost including buyer's fee

        Args:
            winning_bid: The hammer price (winning bid amount)

        Returns:
            Dict with breakdown of costs
        """
        buyer_fee = int(winning_bid * FeeCalculator.BUYER_FEE_PERCENT)
        total_cost = winning_bid + buyer_fee

        return {
            'winning_bid': winning_bid,
            'buyer_fee': buyer_fee,
            'buyer_fee_percent': FeeCalculator.BUYER_FEE_PERCENT * 100,
            'total_cost': total_cost,
            'fee_per_dollar': round(FeeCalculator.BUYER_FEE_PERCENT * 100, 2)
        }

    @staticmethod
    def calculate_max_bid(target_price: int) -> dict:
        """
        Calculate max bid to stay within target price (including fees)

        If you want to pay max $35,000 total, what's your max bid?

        Args:
            target_price: Maximum total amount willing to pay

        Returns:
            Dict with max bid and resulting total cost
        """
        # target_price = winning_bid * (1 + fee_percent)
        # winning_bid = target_price / (1 + fee_percent)

        fee_multiplier = 1 + FeeCalculator.BUYER_FEE_PERCENT
        max_bid = int(target_price / fee_multiplier)
        resulting_cost = max_bid * fee_multiplier

        return {
            'target_price': target_price,
            'max_bid': max_bid,
            'resulting_total_cost': resulting_cost,
            'fee_amount': resulting_cost - max_bid,
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
