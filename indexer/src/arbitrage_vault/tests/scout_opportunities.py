import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to sys.path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from arbitrage_vault.agent.arbitrage import detect_arbitrage
from arbitrage_vault.agent.arbitrage import evaluate_profitability
from arbitrage_vault.utils import discover_pools
from arbitrage_vault.utils import extract_prices
from arbitrage_vault.utils import get_gas_price
from arbitrage_vault.utils import get_xtz_price

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Scout')


async def scout():
    rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')

    logger.info('🔎 Scouting for arbitrage opportunities on Etherlink...')

    # 1. Fetch Prices and Gas
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)

    logger.info('Native Price: $%.4f', xtz_price)
    logger.info('Gas Price: %.2f gwei', gas_price / 10**9)

    # 2. Discover Pools
    pools = await discover_pools(max_pages=5)
    if not pools:
        logger.warning('No pools found.')
        return

    logger.info('Scanned %d pools.', len(pools))

    # 3. Detect Arbitrage
    price_map = extract_prices(pools)
    opportunities = detect_arbitrage(price_map)

    if not opportunities:
        logger.info('No arbitrage spreads detected.')
        return

    # 4. Evaluate Profitability
    evaluations = await evaluate_profitability(
        opportunities,
        xtz_price_usd=xtz_price,
        gas_price_wei=gas_price,
        min_profit_margin=0.001,  # Show everything above 0.1% for scouting
    )

    # 5. Print Results
    print('\n' + '=' * 80)
    print(f'{"PAIR":<20} | {"SPREAD %":<10} | {"GROSS PROFIT":<15} | {"NET PROFIT":<15} | {"DECISION"}')
    print('-' * 80)

    profitable_count = 0
    for ev in evaluations:
        opp = ev['opportunity']
        decision = ev['decision']
        net_profit = ev['net_profit_usd']

        if decision == 'EXECUTE':
            profitable_count += 1
            color_start = '\033[92m'  # Green
            color_end = '\033[0m'
        else:
            color_start = ''
            color_end = ''

        print(
            f'{color_start}{opp["pair_id"]:<20} | {opp["spread_pct"] * 100:>8.3f}% | ${opp["estimated_gross_profit"]:>13.4f} | ${net_profit:>13.4f} | {decision}{color_end}'
        )

    print('=' * 80)
    logger.info('Found %d profitable opportunities out of %d total spreads.', profitable_count, len(opportunities))


if __name__ == '__main__':
    asyncio.run(scout())
