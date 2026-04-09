import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Configurable constants
GAS_PER_SWAP = 1_500_000
MIN_TVL_THRESHOLD = 1000.0

# Canonical WXTZ address (lowercase)
WXTZ_ADDRESS = os.getenv('WXTZ_ADDRESS', '0xc9b53ab2679f573e480d01e0f49e2b5cfb7a3eab')

# ---------------------------------------------------------------------------
# Trade sizing configuration
# ---------------------------------------------------------------------------
# Realistic USD amounts to test for each route.
# The bot simulates each amount and picks the one with the highest net profit.
# Override via env: TRADE_AMOUNTS_USD=10,50,100,500,1000,5000
_TRADE_AMOUNTS_RAW = os.getenv('TRADE_AMOUNTS_USD', '10,50,100,500,1000,5000')
DEFAULT_TRADE_AMOUNTS = [float(x.strip()) for x in _TRADE_AMOUNTS_RAW.split(',') if x.strip()]

# Safety cap: never trade more than this % of the route's smallest pool TVL
MAX_TRADE_PCT_OF_TVL = float(os.getenv('MAX_TRADE_PCT_OF_TVL', '0.10'))  # 10%

# Max hops for cycle search
DEFAULT_MAX_HOPS = 4


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------


def build_pool_graph(pools: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Build a directed token graph from all pools.
    Each node is a lowercase token address.
    Each edge: {'to': addr, 'pool': pool, 'direction': 0|1}
    """
    graph: dict[str, list[dict[str, Any]]] = {}
    pool_count = 0
    for pool in pools:
        t0 = pool['token0']['address'].lower()
        t1 = pool['token1']['address'].lower()
        graph.setdefault(t0, []).append({'to': t1, 'pool': pool, 'direction': 0})
        graph.setdefault(t1, []).append({'to': t0, 'pool': pool, 'direction': 1})
        pool_count += 1

    unique_tokens = len(graph.keys())
    total_edges = sum(len(edges) for edges in graph.values())
    logger.info(
        '📊 Graph Status: %d pools, %d unique tokens, %d directed edges', pool_count, unique_tokens, total_edges
    )
    return graph


# ---------------------------------------------------------------------------
# AMM simulation using real token USD prices
# ---------------------------------------------------------------------------


def simulate_hop(amount_in_usd: float, pool: dict[str, Any], direction: int) -> float:
    """
    Simulate a single AMM swap using constant-product formula.
    Uses per-token price_usd (from GeckoTerminal) for accurate reserve estimation.
    Returns the USD value of the output amount.
    """
    tvl = pool.get('tvl_usd', 0.0)
    fee = pool.get('fee', 0.3) / 100.0  # e.g. 0.3% → 0.003

    if tvl <= 0 or amount_in_usd <= 0:
        return 0.0

    if direction == 0:
        in_token = pool['token0']
        out_token = pool['token1']
    else:
        in_token = pool['token1']
        out_token = pool['token0']

    price_in = in_token.get('price_usd', 0.0)
    price_out = out_token.get('price_usd', 0.0)

    if price_in > 0 and price_out > 0:
        # Accurate simulation using real USD prices
        # Reserves in token units (assume 50/50 TVL split)
        reserve_in_tokens = (tvl / 2.0) / price_in
        reserve_out_tokens = (tvl / 2.0) / price_out

        # Convert input USD → token units
        amount_in_tokens = amount_in_usd / price_in
        amount_in_eff = amount_in_tokens * (1.0 - fee)

        # Constant-product: out = (eff_in * reserve_out) / (reserve_in + eff_in)
        if reserve_in_tokens + amount_in_eff <= 0:
            return 0.0

        amount_out_tokens = (amount_in_eff * reserve_out_tokens) / (reserve_in_tokens + amount_in_eff)
        return amount_out_tokens * price_out
    # Fallback: pure USD-space approximation (no price data available)
    reserve_in_usd = tvl / 2.0
    reserve_out_usd = tvl / 2.0
    amount_in_eff = amount_in_usd * (1.0 - fee)

    if reserve_in_usd + amount_in_eff <= 0:
        return 0.0

    return (amount_in_eff * reserve_out_usd) / (reserve_in_usd + amount_in_eff)


def simulate_route(route: list[dict[str, Any]], trade_size_usd: float) -> float:
    """
    Simulate the full return of a multi-hop route.
    Returns final USD value starting from trade_size_usd.
    """
    amount = trade_size_usd
    for hop in route:
        amount = simulate_hop(amount, hop['pool'], hop['direction'])
        if amount <= 0:
            return 0.0
    return amount


# ---------------------------------------------------------------------------
# Cycle detection — anchor to vault token or search all
# ---------------------------------------------------------------------------


def find_cycles_from(
    graph: dict[str, list[dict[str, Any]]],
    start_token: str,
    max_hops: int = DEFAULT_MAX_HOPS,
) -> list[list[dict[str, Any]]]:
    """
    DFS from start_token to find all simple cycles that return to start_token.
    """
    cycles: list[list[dict[str, Any]]] = []

    def dfs(current: str, path: list[dict[str, Any]], visited_pools: set[str]):
        if len(path) > max_hops:
            return
        for edge in graph.get(current, []):
            pool_addr = edge['pool']['address'].lower()
            next_token = edge['to']
            if pool_addr in visited_pools:
                continue
            new_path = [*path, edge]
            if next_token == start_token and len(new_path) >= 2:
                cycles.append(new_path)
            else:
                visited_intermediate = {h['to'] for h in path}
                if next_token not in visited_intermediate and next_token != start_token:
                    dfs(next_token, new_path, visited_pools | {pool_addr})

    dfs(start_token, [], set())
    return cycles


def find_all_cycles(
    graph: dict[str, list[dict[str, Any]]],
    max_hops: int = DEFAULT_MAX_HOPS,
    anchor_token: str | None = None,
) -> list[list[dict[str, Any]]]:
    """
    Find all simple cycles across all tokens.
    If anchor_token is provided, ONLY search cycles that start (and end) at that token.
    Otherwise, search all tokens and deduplicate mirrored routes.
    """
    seen_pool_sets: set[frozenset[str]] = set()
    all_cycles: list[list[dict[str, Any]]] = []

    if anchor_token:
        # Focused search: only cycles starting from the vault's asset token
        tokens_to_search = [anchor_token.lower()]
        logger.info('🎯 Anchoring cycle search to vault token: %s', anchor_token)
    else:
        tokens_to_search = list(graph.keys())

    for start_token in tokens_to_search:
        found = find_cycles_from(graph, start_token, max_hops)
        for cycle in found:
            key = frozenset(h['pool']['address'].lower() for h in cycle)
            if key not in seen_pool_sets:
                seen_pool_sets.add(key)
                all_cycles.append(cycle)

    logger.info('🔄 Cycle Discovery: Found %d unique cycles across %d tokens', len(all_cycles), len(tokens_to_search))
    return all_cycles


# ---------------------------------------------------------------------------
# Main detection entry point
# ---------------------------------------------------------------------------


def _route_label(route: list[dict[str, Any]]) -> str:
    """Build a human-readable route string like WXTZ → USDC → stXTZ → WXTZ."""
    symbols = []
    for hop in route:
        pool = hop['pool']
        from_token = pool['token0'] if hop['direction'] == 0 else pool['token1']
        symbols.append(from_token.get('symbol', '???'))
    # append the final token
    last_hop = route[-1]
    end_token = last_hop['pool']['token1'] if last_hop['direction'] == 0 else last_hop['pool']['token0']
    symbols.append(end_token.get('symbol', '???'))
    return ' → '.join(symbols)


def detect_multi_hop_arbitrage(
    pools: list[dict[str, Any]],
    max_hops: int = DEFAULT_MAX_HOPS,
    min_return_pct: float = -0.05,
    asset_token_address: str | None = None,
    trade_amounts: list[float] | None = None,
) -> list[dict[str, Any]]:
    """
    Find all profitable arbitrage routes.
    If asset_token_address is provided, only search cycles that start (and end)
    at that token — matching the vault's actual held asset.
    Profit is always expressed in USD using price_usd from the pool cache.

    Trade sizing: Tests each amount in trade_amounts (default: DEFAULT_TRADE_AMOUNTS)
    and picks the one with the highest net USD profit.
    Each amount is capped at MAX_TRADE_PCT_OF_TVL of the route's smallest pool.
    """
    graph = build_pool_graph(pools)

    # Resolve anchor: use provided asset address (lowercased) or search all
    anchor = asset_token_address.lower() if asset_token_address else None
    if anchor and anchor not in graph:
        logger.warning('⚠️  Vault asset %s not found in pool graph — falling back to all-token search', anchor)
        anchor = None

    all_cycles = find_all_cycles(graph, max_hops, anchor_token=anchor)
    logger.info('🔎 Checking %d unique cycles for optimal profit...', len(all_cycles))

    amounts_to_test = trade_amounts or DEFAULT_TRADE_AMOUNTS
    logger.info('💵 Testing trade amounts: %s', ', '.join(f'${a:,.0f}' for a in amounts_to_test))

    opportunities = []
    for route in all_cycles:
        # 1. Calculate Theoretical Spread (Near-zero slippage)
        # Using $0.01 as a proxy for infinitesimal trade size
        theoretical_out = simulate_route(route, 0.01)
        spread_pct = (theoretical_out - 0.01) / 0.01 if theoretical_out > 0 else -1.0

        # 2. Determine max safe trade size from route liquidity
        min_pool_tvl = min(h['pool'].get('tvl_usd', 0.0) for h in route)
        if min_pool_tvl <= 0.1:
            continue

        max_safe_amount = min_pool_tvl * MAX_TRADE_PCT_OF_TVL

        # 3. Test each trade amount and find the best one
        best_size = 0.0
        best_profit = -999999.0
        best_out = 0.0

        for raw_amount in amounts_to_test:
            # Cap amount at the safe maximum for this route
            size = min(raw_amount, max_safe_amount)
            if size < 0.01:
                continue

            output = simulate_route(route, size)
            profit = output - size
            if profit > best_profit:
                best_profit = profit
                best_size = size
                best_out = output

        if best_size <= 0:
            continue

        return_pct = best_profit / best_size
        if return_pct <= min_return_pct:
            continue

        total_fee_pct = sum(h['pool'].get('fee', 0.3) for h in route)
        has_low_liquidity = min_pool_tvl < MIN_TVL_THRESHOLD

        route_str = _route_label(route)
        is_direct = len(route) == 2

        opportunities.append(
            {
                'pair_id': route_str,
                'route': route,
                'hops': len(route),
                'return_pct': return_pct,
                'spread_pct': spread_pct,  # Raw price spread (no slippage)
                'estimated_gross_profit': best_profit,
                'input_amount_usd': best_size,
                'output_amount_usd': best_out,
                'total_fee_pct': total_fee_pct,
                'is_direct': is_direct,
                'has_low_liquidity': has_low_liquidity,
                'min_pool_tvl': min_pool_tvl,
                # Legacy execution keys
                'buy_pool': route[0]['pool'] if is_direct else None,
                'sell_pool': route[1]['pool'] if is_direct else None,
                'base_token': route[0]['pool']['token0'] if route[0]['direction'] == 0 else route[0]['pool']['token1'],
                'quote_token': route[0]['pool']['token1'] if route[0]['direction'] == 0 else route[0]['pool']['token0'],
            }
        )

    return sorted(opportunities, key=lambda x: x['estimated_gross_profit'], reverse=True)


# ---------------------------------------------------------------------------
# Legacy pairwise engine (kept for compatibility)
# ---------------------------------------------------------------------------


def detect_arbitrage(price_map: dict[str, list[dict[str, Any]]], min_spread_pct: float = 0.0) -> list[dict[str, Any]]:
    """Legacy pairwise arbitrage detection. Use detect_multi_hop_arbitrage instead."""
    opportunities = []
    for pair_id, prices in price_map.items():
        if len(prices) < 2:
            continue
        for i in range(len(prices)):
            for j in range(i + 1, len(prices)):
                a, b = prices[i], prices[j]
                buy, sell = (a, b) if a['price'] < b['price'] else (b, a)
                spread = (sell['price'] - buy['price']) / buy['price']
                if spread <= min_spread_pct:
                    continue
                trade_size = min(buy['pool']['tvl_usd'], sell['pool']['tvl_usd']) * 0.01
                opportunities.append(
                    {
                        'pair_id': pair_id,
                        'base_token': buy['base_token'],
                        'quote_token': buy['quote_token'],
                        'buy_pool': buy['pool'],
                        'buy_price': buy['price'],
                        'sell_pool': sell['pool'],
                        'sell_price': sell['price'],
                        'spread_pct': spread,
                        'return_pct': spread,
                        'estimated_gross_profit': trade_size * spread,
                        'input_amount_usd': trade_size,
                        'output_amount_usd': trade_size * (1 + spread),
                        'total_fee_pct': 0.6,
                        'is_direct': True,
                        'hops': 2,
                    }
                )
    return sorted(opportunities, key=lambda x: x['spread_pct'], reverse=True)


async def evaluate_profitability(
    opportunities: list[dict[str, Any]],
    xtz_price_usd: float,
    gas_price_wei: int,
    min_profit_margin: float = 0.005,
    max_slippage: float = 0.01,
) -> list[dict[str, Any]]:
    """
    Evaluate profitability accounting for gas costs and slippage.
    Multi-hop routes (3+ legs) are marked SCOUT — visible but not executed.
    """
    evaluations = []
    for opp in opportunities:
        hops = opp.get('hops', 2)
        gas_cost_usd = (gas_price_wei * GAS_PER_SWAP * hops / 10**18) * xtz_price_usd

        slippage_adj = opp['estimated_gross_profit'] * (1 - max_slippage)
        fee_buffer = opp['estimated_gross_profit'] * 0.003
        net_profit_usd = slippage_adj - gas_cost_usd - fee_buffer

        decision = 'SKIP'
        reason = ''

        if not opp.get('is_direct', True):
            if os.getenv('ALLOW_MULTI_HOP_EXECUTION') == 'true':
                if net_profit_usd > 0:
                    decision = 'EXECUTE'
                    reason = f'Multi-hop profitable: ${net_profit_usd:.4f} net'
                else:
                    decision = 'SKIP'
                    reason = f'Multi-hop unprofitable: ${net_profit_usd:.4f}'
            else:
                decision = 'SCOUT'
                reason = f'Multi-hop ({hops} legs) — detection only, execution pending'
        elif net_profit_usd <= 0:
            reason = f'Negative net profit: ${net_profit_usd:.4f} (Gas: ${gas_cost_usd:.4f})'
        elif opp.get('return_pct', 0) < min_profit_margin:
            reason = f'Return {opp["return_pct"] * 100:.3f}% < min {min_profit_margin * 100:.1f}%'
        elif opp.get('has_low_liquidity'):
            reason = f'Low liquidity on route (TVL < ${MIN_TVL_THRESHOLD})'
        else:
            decision = 'EXECUTE'
            reason = f'Profitable: ${net_profit_usd:.4f} net after gas'

        evaluations.append(
            {
                'opportunity': opp,
                'net_profit_usd': net_profit_usd,
                'gas_cost_usd': gas_cost_usd,
                'decision': decision,
                'reason': reason,
            }
        )

    return evaluations
