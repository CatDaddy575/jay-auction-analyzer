"""
BringATrailer fee calculator
Accurately calculates buyer's fees and total cost
"""

class FeeCalculator:
    """Calculate BringATrailer buyer's fees"""

    # BringATrailer fee structure (verified from https://bringatrailer.com/help/buying/)
    # Category-based fees (5% or 10% depending on auction category):
    # - Minimum fee: $250
    # - 10% fee cap: $4,000
    # - 5% fee cap: $7,500
    # Note: We default to 5% (most common); user can override for 10% auctions

    FEE_RATE_5_PERCENT = 0.05
    FEE_RATE_10_PERCENT = 0.10
    MIN_FEE = 250
    CAP_5_PERCENT = 7_500
    CAP_10_PERCENT = 4_000

    @staticmethod
    def calculate_total_cost(winning_bid: int, fee_rate: float = 0.05) -> dict:
        """
        Calculate total cost including buyer's fee

        Args:
            winning_bid: The hammer price (winning bid amount)
            fee_rate: Fee rate (0.05 for 5% or 0.10 for 10%), defaults to 5%

        Returns:
            Dict with breakdown of costs
        """
        # Calculate fee
        buyer_fee = int(winning_bid * fee_rate)

        # Apply minimum fee
        if buyer_fee < FeeCalculator.MIN_FEE:
            buyer_fee = FeeCalculator.MIN_FEE

        # Apply appropriate cap
        if fee_rate == 0.10:
            if buyer_fee > FeeCalculator.CAP_10_PERCENT:
                buyer_fee = FeeCalculator.CAP_10_PERCENT
                fee_capped = True
            else:
                fee_capped = False
        else:  # 5%
            if buyer_fee > FeeCalculator.CAP_5_PERCENT:
                buyer_fee = FeeCalculator.CAP_5_PERCENT
                fee_capped = True
            else:
                fee_capped = False

        total_cost = winning_bid + buyer_fee
        actual_fee_rate = (buyer_fee / winning_bid * 100) if winning_bid > 0 else 0

        return {
            'winning_bid': winning_bid,
            'buyer_fee': buyer_fee,
            'buyer_fee_percent': actual_fee_rate,
            'total_cost': total_cost,
            'fee_per_dollar': round(actual_fee_rate, 2),
            'fee_capped': fee_capped,
            'category': '10%' if fee_rate == 0.10 else '5%'
        }

    @staticmethod
    def calculate_max_bid(target_price: int, fee_rate: float = 0.05) -> dict:
        """
        Calculate max bid to stay within target price (including buyer's fee)

        If you want to pay max $35,000 total, what's your max bid?

        Args:
            target_price: Maximum total amount willing to pay
            fee_rate: Fee rate (0.05 for 5% or 0.10 for 10%), defaults to 5%

        Returns:
            Dict with max bid and resulting total cost
        """
        max_bid = target_price

        for _ in range(100):
            cost_calc = FeeCalculator.calculate_total_cost(max_bid, fee_rate)
            if cost_calc['total_cost'] <= target_price:
                break
            max_bid -= 50

        resulting_calc = FeeCalculator.calculate_total_cost(max_bid, fee_rate)

        return {
            'target_price': target_price,
            'max_bid': max_bid,
            'resulting_total_cost': resulting_calc['total_cost'],
            'fee_amount': resulting_calc['buyer_fee'],
            'fee_capped': resulting_calc['fee_capped'],
            'category': resulting_calc['category'],
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
