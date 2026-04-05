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
from arbitrage_vault.utils import discover_pools, extract_prices, get_xtz_price, get_gas_price
from arbitrage_vault.agent.arbitrage import detect_arbitrage, evaluate_profitability
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
    print("SCOUTING FOR OPPORTUNITIES (5 Pages)")
    print("="*80)
    
    rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)
    
    pools = await discover_pools(max_pages=5)
    if not pools:
        print("No pools found.")
        return
        
    price_map = extract_prices(pools)
    opportunities = detect_arbitrage(price_map)
    
    if not opportunities:
        print("No arbitrage spreads detected.")
        return

    # Preliminary evaluation for the table
    evals = await evaluate_profitability(
        opportunities, 
        xtz_price_usd=xtz_price, 
        gas_price_wei=gas_price,
        min_profit_margin=0.001
    )

    print(f'{"PAIR":<20} | {"SPREAD %":<10} | {"GROSS $":<10} | {"NET $":<10} | {"DECISION"}')
    print('-' * 80)
    for ev in evals:
        opp = ev['opportunity']
        color = '\033[92m' if ev['decision'] == 'EXECUTE' else ''
        reset = '\033[0m' if color else ''
        print(f'{color}{opp["pair_id"]:<20} | {opp["spread_pct"]*100:>8.2f}% | {opp["estimated_gross_profit"]:>10.4f} | {ev["net_profit_usd"]:>10.4f} | {ev["decision"]}{reset}')
    print("="*80 + "\n")

    # 4. Run the arbitrage hook with discovered opportunities
    ctx = MockHookContext()
    vault_address = os.getenv('VAULT_ADDRESS', '0x895Ea1c1A1EF1EceF0Fb822e33BE0bB9d493559d')
    
    print(f"Starting agent review for vault {vault_address}...")
    try:
        async with transactions.in_transaction():
            await run_arbitrage(ctx, vault_address, min_profit_usd=0.01, opportunities=opportunities)
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
