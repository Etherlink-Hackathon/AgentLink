import asyncio
import os
import sys
import logging
from decimal import Decimal
from tortoise import Tortoise, transactions

# Load environment variables
from dotenv import load_dotenv

# Ensure we can import from src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from arbitrage_vault.hooks.run_arbitrage import run_arbitrage
from arbitrage_vault.utils import discover_pools, get_xtz_price, get_gas_price
from arbitrage_vault.agent.arbitrage import detect_multi_hop_arbitrage, evaluate_profitability
from arbitrage_vault.models import AgentDecision
import dipdup.models

# Monkey-patch DipDup to allow standalone execution without its TransactionManager
dipdup.models.get_transaction = lambda: None
dipdup.models.get_pending_updates = lambda: []

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock HookContext for standalone execution
class MockHookContext:
    def __init__(self):
        self.logger = logger
    
    async def execute_sql(self, sql):
        logger.info(f"SQL execute (mocked): {sql}")

async def run_standalone():
    # 1. Load configuration
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(env_path)
    
    user = os.getenv('POSTGRES_USER', 'huydo')
    password = os.getenv('POSTGRES_PASSWORD', 'huydo2105')
    db_name = os.getenv('POSTGRES_DB', 'huydo')
    host = 'localhost' 
    port = '5433' # Port 5433 is mapped to 5432 in docker-compose.yml
    
    db_url = f'postgres://{user}:{password}@{host}:{port}/{db_name}'
    print(f"Connecting to database with URL: postgres://{user}:****@{host}:{port}/{db_name}")
    
    # 2. Initialize Tortoise ORM
    print(f"Connecting to database at {host}:{port}...")
    try:
        await Tortoise.init(
            db_url=db_url,
            modules={'models': ['arbitrage_vault.models']}
        )
        print("Connected to database.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    # 3. Scouting Phase (from scout_opportunities.py)
    print("\n" + "🔎 " + "="*76)
    print("SCOUTING FOR OPPORTUNITIES (15 Pages)")
    print("="*80)
    
    rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)
    
    pools = await discover_pools(max_pages=15, force_refresh=True)
    if not pools:
        print("No pools found.")
        return

    opportunities = detect_multi_hop_arbitrage(pools)

    if not opportunities:
        print("No arbitrage routes detected.")
        return

    # Preliminary evaluation for the table
    evals = await evaluate_profitability(
        opportunities,
        xtz_price_usd=xtz_price,
        gas_price_wei=gas_price,
        min_profit_margin=0.001
    )

    print(f'{"ROUTE":<45} | {"HOPS":>4} | {"TYPE":<6} | {"SPREAD %":>8} | {"RETURN %":>8} | {"INPUT $":>8} | {"OUTPUT $":>9} | {"GAS $":>7} | {"NET $":>9} | {"FEES%":>5} | DECISION')
    print('-' * 175)
    for ev in evals:
        opp = ev['opportunity']
        decision = ev['decision']
        route_type = 'DIRECT' if opp.get('is_direct') else 'SCOUT'
        if decision == 'EXECUTE':
            color = '\033[92m'   # green
        elif decision == 'SCOUT':
            color = '\033[94m'   # blue
        elif ev['net_profit_usd'] < 0:
            color = '\033[91m'   # red
        else:
            color = '\033[93m'   # yellow (skip)
        reset = '\033[0m'
        route_label = opp['pair_id'][:43]
        print(
            f"{color}{route_label:<45} | {opp.get('hops', 2):>4} | {route_type:<6} | "
            f"{opp.get('spread_pct', 0)*100:>7.3f}% | {opp.get('return_pct', 0)*100:>7.3f}% | "
            f"{opp.get('input_amount_usd', 0):>8.2f} | {opp.get('output_amount_usd', 0):>9.2f} | "
            f"{ev.get('gas_cost_usd', 0):>7.4f} | {ev['net_profit_usd']:>9.4f} | "
            f"{opp.get('total_fee_pct', 0):>5.2f}% | {decision}{reset}"
        )
    print("="*175 + "\n")

    # Only pass direct (2-leg) opportunities to the agent for execution
    direct_opportunities = [opp for opp in opportunities if opp.get('is_direct')]

    # 4. Run the arbitrage hook with discovered opportunities
    ctx = MockHookContext()
    vault_address = os.getenv('VAULT_ADDRESS', '0x895Ea1c1A1EF1EceF0Fb822e33BE0bB9d493559d')
    
    print(f"Starting agent review for vault {vault_address}...")
    try:
        async with transactions.in_transaction():
            await run_arbitrage(ctx, vault_address, min_profit_usd=0.01, opportunities=direct_opportunities)
        print("Agent review cycle completed successfully.")

        # 5. Execution Phase (NEW)
        print("\n" + "🚀 " + "="*76)
        print("EXECUTING APPROVED DECISIONS")
        print("="*80)
        
        # We need to import AgentExecutor from on_synchronized
        from arbitrage_vault.hooks.on_synchronized import AgentExecutor
        
        # Initialize executor (it will pick up env vars)
        try:
            executor = AgentExecutor.get_instance()
            
            # Fetch pending 'EXECUTE' decisions
            pending = await AgentDecision.filter(status='EXECUTE').all()
            if not pending:
                print("No decisions marked for direct execution.")
            else:
                print(f"Found {len(pending)} decisions ready for execution.")
                for decision in pending:
                    print(f"Processing decision {decision.id} for {decision.opportunity_details.get('pair_id')}...")
                    await executor.process_decision(decision.id)
                    
                    # Refresh from DB to see result
                    await decision.refresh_from_db()
                    status_color = '\033[92m' if decision.status == 'SENT' else '\033[91m'
                    print(f"Decision {decision.id} result: {status_color}{decision.status}{reset}")
                    if decision.tx_hash:
                        print(f"Transaction Hash: {decision.tx_hash}")
                    if decision.error:
                        print(f"Error: {decision.error}")
        except Exception as exec_err:
            print(f"Executor initialization/processing failed: {exec_err}")
            
        print("="*80 + "\n")
    except Exception as e:
        print(f"Error during arbitrage run: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(run_standalone())
