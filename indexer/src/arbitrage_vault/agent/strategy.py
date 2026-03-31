import logging
from typing import Any

logger = logging.getLogger(__name__)


class ArbitrageHeuristics:
    """
    Core mathematical invariants and safety checks for arbitrage.
    """

    def __init__(self, min_profit_usd: float = 0.1, max_slippage_bps: int = 50):
        self.min_profit_usd = min_profit_usd
        self.max_slippage_bps = max_slippage_bps

    def evaluate(self, opportunity: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate if an opportunity meets the minimum viability thresholds.
        """
        net_profit = opportunity.get('net_profit_usd', 0)
        spread_pct = opportunity.get('spread_pct', 0)

        # 1. Profitability Floor
        if net_profit < self.min_profit_usd:
            return {
                'verdict': 'REJECT',
                'reason': f'Profit ${net_profit:.4f} below floor ${self.min_profit_usd}',
                'confidence': 1.0,
            }

        # 2. Spread Quality Check
        if spread_pct < 0.05:  # 0.05%
            return {'verdict': 'REJECT', 'reason': f'Spread {spread_pct:.4f}% too tight', 'confidence': 0.9}

        # 3. Path Sanitation
        if not opportunity.get('buy_pool') or not opportunity.get('sell_pool'):
            return {'verdict': 'REJECT', 'reason': 'Incomplete path data', 'confidence': 1.0}

        return {
            'verdict': 'APPROVE',
            'reason': 'Profitability and spread invariants met.',
            'confidence': 1.0,
            'params': {'max_gas_premium_pct': 20, 'slippage_bps': self.max_slippage_bps},
        }
