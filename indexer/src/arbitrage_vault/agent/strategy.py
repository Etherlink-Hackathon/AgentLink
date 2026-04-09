import logging
from typing import Any

logger = logging.getLogger(__name__)


class ArbitrageHeuristics:
    """
    Core mathematical invariants and safety checks for arbitrage.
    """

    def __init__(self, min_profit_usd: float = 0.001, max_slippage_bps: int = 50):
        self.min_profit_usd = min_profit_usd
        self.max_slippage_bps = max_slippage_bps

    def evaluate(self, opportunity: dict[str, Any], strategy_config: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Evaluate if an opportunity meets the minimum viability thresholds.
        """
        # Load config with defaults
        config = strategy_config or {}
        min_p = config.get('min_profit_usd', self.min_profit_usd)
        slippage = config.get('max_slippage_bps', self.max_slippage_bps)

        net_profit = opportunity.get('net_profit_usd', 0)
        spread_pct = opportunity.get('spread_pct', 0)

        # 1. Profitability Floor
        if net_profit < min_p:
            logger.info('Profit $%.4f below floor $%.4f', net_profit, min_p)
            return {
                'verdict': 'REJECT',
                'reason': f'Profit ${net_profit:.4f} below floor ${min_p:.4f}',
                'confidence': 1.0,
            }

        # 2. Spread Quality Check
        # GeckoTerminal uses 0.0001 for 0.01%.
        if spread_pct < 0.0001:  # 0.01%
            logger.info('Spread %.4f%% too tight', spread_pct * 100)
            return {'verdict': 'REJECT', 'reason': f'Spread {spread_pct * 100:.4f}% too tight', 'confidence': 0.9}

        # 3. Path Sanitation (for 2-leg direct routes only)
        if not opportunity.get('route') and (not opportunity.get('buy_pool') or not opportunity.get('sell_pool')):
            logger.info('Incomplete path data')
            return {'verdict': 'REJECT', 'reason': 'Incomplete path data', 'confidence': 1.0}

        return {
            'verdict': 'APPROVE',
            'reason': 'Profitability and spread invariants met.',
            'confidence': 1.0,
            'params': {'max_gas_premium_pct': 20, 'slippage_bps': slippage},
        }
