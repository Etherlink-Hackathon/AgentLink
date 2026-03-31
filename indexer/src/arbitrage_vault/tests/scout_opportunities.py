import asyncio
import logging
import os
import sys

# Add the src directory to sys.path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from arbitrage_vault.agent.arbitrage import detect_arbitrage, evaluate_profitability
from arbitrage_vault.utils import discover_pools, extract_prices, get_gas_price, get_xtz_price

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Scout')

async def scout():
    rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')
    
    logger.info("🔎 Scouting for arbitrage opportunities on Etherlink...")
    
    # 1. Fetch Prices and Gas
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)
    
    logger.info(f"Native Price: ${xtz_price:.4f}")
    logger.info(f"Gas Price: {gas_price / 10**9:.2f} gwei")
    
    # 2. Discover Pools
    pools = await discover_pools(max_pages=5)
    if not pools:
        logger.warning("No pools found.")
        return
        
    logger.info(f"Scanned {len(pools)} pools.")
    
    # 3. Detect Arbitrage
    price_map = extract_prices(pools)
    opportunities = detect_arbitrage(price_map)
    
    if not opportunities:
        logger.info("No arbitrage spreads detected.")
        return
        
    # 4. Evaluate Profitability
    evaluations = await evaluate_profitability(
        opportunities, 
        xtz_price_usd=xtz_price, 
        gas_price_wei=gas_price,
        min_profit_margin=0.001 # Show everything above 0.1% for scouting
    )
    
    # 5. Print Results
    print("\n" + "="*80)
    print(f"{'PAIR':<20} | {'SPREAD %':<10} | {'GROSS PROFIT':<15} | {'NET PROFIT':<15} | {'DECISION'}")
    print("-" * 80)
    
    profitable_count = 0
    for ev in evaluations:
        opp = ev['opportunity']
        decision = ev['decision']
        net_profit = ev['net_profit_usd']
        
        if decision == 'EXECUTE':
            profitable_count += 1
            color_start = "\033[92m" # Green
            color_end = "\033[0m"
        else:
            color_start = ""
            color_end = ""
            
        print(f"{color_start}{opp['pair_id']:<20} | {opp['spread_pct']*100:>8.3f}% | ${opp['estimated_gross_profit']:>13.4f} | ${net_profit:>13.4f} | {decision}{color_end}")
        
    print("="*80)
    logger.info(f"Found {profitable_count} profitable opportunities out of {len(opportunities)} total spreads.")

if __name__ == "__main__":
    asyncio.run(scout())
