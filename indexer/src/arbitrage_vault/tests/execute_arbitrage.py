import asyncio
import logging
import os
import sys
from decimal import Decimal

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tortoise import Tortoise
from arbitrage_vault.agent.arbitrage import detect_arbitrage, evaluate_profitability
from arbitrage_vault.utils import discover_pools, extract_prices, get_gas_price, get_xtz_price
from arbitrage_vault.models import Agent, AgentDecision, Vault

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Executor')

async def init_db():
    db_url = f"postgres://{os.getenv('POSTGRES_USER', 'huydo')}:{os.getenv('POSTGRES_PASSWORD', 'huydo2105')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'huydo')}"
    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['arbitrage_vault.models']}
    )

async def run_execution():
    rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')
    vault_address = os.getenv('VAULT_ADDRESS', '0x895Ea1c1A1EF1EceF0Fb822e33BE0bB9d493559d')
    strategist_address = os.getenv('STRATEGIST_ADDRESS', '0x0000000000000000000000000000000000000000')

    await init_db()
    
    logger.info("🚀 Starting Manual Arbitrage Execution Process...")
    
    # 1. Fetch context
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)
    
    vault = await Vault.get_or_none(address=vault_address)
    if not vault:
        logger.error(f"Vault {vault_address} not found in database. Please run indexer first.")
        return

    agent, _ = await Agent.get_or_create(
        address=strategist_address,
        vault=vault,
        defaults={
            'name': 'Manual Test Agent',
            'details': {'role': 'TESTER'},
            'strategy_config': {'min_profit_usd': 0.1, 'max_slippage_bps': 50}
        }
    )

    # 2. Find opportunities
    pools = await discover_pools(max_pages=3)
    price_map = extract_prices(pools)
    opportunities = detect_arbitrage(price_map)
    evaluations = await evaluate_profitability(
        opportunities, 
        xtz_price_usd=xtz_price, 
        gas_price_wei=gas_price,
        min_profit_margin=0.0001 # Be aggressive for testing
    )
    
    # 3. Filter for profitable
    profitable = [ev for ev in evaluations if ev['decision'] == 'EXECUTE']
    
    if not profitable:
        logger.warning("No profitable opportunities found right now. Try again later or lower profit thresholds.")
        # Optional: Force execute the best one for testing
        if evaluations:
            logger.info("FORCING execution of the best available opportunity for testing...")
            best_ev = evaluations[0]
        else:
            return
    else:
        best_ev = profitable[0]
        
    opp = best_ev['opportunity']
    
    # 4. Create Decision
    logger.info(f"🔔 Creating execution decision for {opp['pair_id']} (Expected Profit: ${best_ev['net_profit_usd']:.4f})")
    
    decision = await AgentDecision.create(
        vault=vault,
        agent=agent,
        status='EXECUTE', # This triggers the background listener in on_synchronized.py
        heuristics_verdict='APPROVE',
        opportunity_details={
            'pair_id': opp['pair_id'],
            'net_profit_usd': float(best_ev['net_profit_usd']),
            'spread_pct': float(opp['spread_pct']),
            'buy_pool': opp['buy_pool'],
            'sell_pool': opp['sell_pool'],
            'xtz_price': xtz_price,
            'gas_price_gwei': gas_price / 10**9,
        }
    )
    
    logger.info(f"✅ Decision {decision.id} created with status EXECUTE.")
    logger.info("Waiting for AgentExecutor to pick it up...")
    
    # 5. Monitor
    for _ in range(30):
        await asyncio.sleep(2)
        await decision.refresh_from_db()
        if decision.status == 'SENT':
            logger.info(f"🎉 SUCCESS! Arbitrage executed. TX: {decision.tx_hash}")
            break
        elif decision.status == 'FAILED':
            logger.error(f"❌ Execution failed: {decision.error}")
            break
        else:
            logger.info(f"Current status: {decision.status}...")
    else:
        logger.warning("Timeout waiting for execution. Is the indexer running?")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run_execution())
