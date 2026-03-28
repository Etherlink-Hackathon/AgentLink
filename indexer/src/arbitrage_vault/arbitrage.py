import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configurable constants (fallbacks if dynamic fetching fails)
DEFAULT_XTZ_PRICE_USD = 1.0
GAS_PER_SWAP = 150_000
SWAPS_PER_ARB = 2
MIN_TVL_THRESHOLD = 1000.0

def detect_arbitrage(price_map: Dict[str, List[Dict[str, Any]]], min_spread_pct: float = 0.0) -> List[Dict[str, Any]]:
    """
    Detect arbitrage opportunities.
    """
    opportunities = []
    
    for pair_id, prices in price_map.items():
        if len(prices) < 2:
            continue
            
        for i in range(len(prices)):
            for j in range(i + 1, len(prices)):
                a = prices[i]
                b = prices[j]
                
                buy, sell = (a, b) if a["price"] < b["price"] else (b, a)
                spread = (sell["price"] - buy["price"]) / buy["price"]
                
                if spread <= min_spread_pct:
                    continue
                    
                trade_size = min(buy["pool"]["tvl_usd"], sell["pool"]["tvl_usd"]) * 0.01
                gross_profit = trade_size * spread
                
                opportunities.append({
                    "pair_id": pair_id,
                    "base_token": buy["base_token"],
                    "quote_token": buy["quote_token"],
                    "buy_pool": buy["pool"],
                    "buy_price": buy["price"],
                    "sell_pool": sell["pool"],
                    "sell_price": sell["price"],
                    "spread_pct": spread,
                    "estimated_gross_profit": gross_profit
                })
                
    return sorted(opportunities, key=lambda x: x["spread_pct"], reverse=True)

async def evaluate_profitability(
    opportunities: List[Dict[str, Any]], 
    xtz_price_usd: float,
    gas_price_wei: int,
    min_profit_margin: float = 0.005,
    max_slippage: float = 0.01
) -> List[Dict[str, Any]]:
    """
    Evaluate profitability using dynamic price and gas data.
    """
    evaluations = []
    
    total_gas_units = GAS_PER_SWAP * SWAPS_PER_ARB
    gas_cost_wei = gas_price_wei * total_gas_units
    gas_cost_xtz = gas_cost_wei / 10**18
    gas_cost_usd = gas_cost_xtz * xtz_price_usd
    
    for opp in opportunities:
        slippage_adjusted_profit = opp["estimated_gross_profit"] * (1 - max_slippage)
        fee_buffer = opp["estimated_gross_profit"] * 0.003
        
        net_profit_usd = slippage_adjusted_profit - gas_cost_usd - fee_buffer
        min_absolute_profit = gas_cost_usd * (1 + min_profit_margin / 0.005)
        
        decision = "SKIP"
        reason = ""
        
        if net_profit_usd <= 0:
            reason = f"Negative net profit: ${net_profit_usd:.4f} (Gas: ${gas_cost_usd:.4f})"
        elif opp["spread_pct"] < min_profit_margin:
            reason = f"Spread {opp['spread_pct']*100:.3f}% < min {min_profit_margin*100:.1f}%"
        elif net_profit_usd < min_absolute_profit:
            reason = f"Net profit ${net_profit_usd:.4f} < threshold ${min_absolute_profit:.4f}"
        elif opp["buy_pool"]["tvl_usd"] < MIN_TVL_THRESHOLD or opp["sell_pool"]["tvl_usd"] < MIN_TVL_THRESHOLD:
            reason = f"Low liquidity (TVL < ${MIN_TVL_THRESHOLD})"
        else:
            decision = "EXECUTE"
            reason = f"Profitable: ${net_profit_usd:.4f} net"
            
        evaluations.append({
            "opportunity": opp,
            "net_profit_usd": net_profit_usd,
            "decision": decision,
            "reason": reason
        })
        
    return evaluations
