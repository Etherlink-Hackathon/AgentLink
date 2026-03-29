import logging
import os
import json
from typing import Any
from dipdup.context import HookContext
from arbitrage_vault.utils import discover_pools, extract_prices, get_xtz_price, get_gas_price
from arbitrage_vault.agent.arbitrage import detect_arbitrage, evaluate_profitability
from arbitrage_vault.models import Vault, Agent, AgentDecision

logger = logging.getLogger(__name__)

async def run_arbitrage(
    ctx: HookContext,
    vault_address: str,
    min_profit_usd: float = 0.1
) -> None:
    """
    Main hook to run an arbitrage cycle for a specific vault.
    Now inserts AgentDecision records for async processing.
    """
    rpc_url = os.getenv("RPC_URL", "https://node.mainnet.etherlink.com")
    strategist_address = os.getenv("STRATEGIST_ADDRESS", "0x0000000000000000000000000000000000000000")
    
    logger.info(f"🚀 Starting arbitrage cycle for vault {vault_address}")
    
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)
    
    vault = await Vault.get_or_none(address=vault_address)
    if not vault:
        logger.error(f"Vault {vault_address} not found. Skipping.")
        return

    pools = await discover_pools()
    if not pools: return
        
    price_map = extract_prices(pools)
    opportunities = detect_arbitrage(price_map)
    evaluations = await evaluate_profitability(
        opportunities, 
        xtz_price_usd=xtz_price,
        gas_price_wei=gas_price,
        min_profit_margin=0.005
    )
    
    agent, _ = await Agent.get_or_create(
        address=strategist_address,
        vault=vault,
        defaults={"name": "Etherlink Soul Agent", "details": {}}
    )
    
    for ev in evaluations:
        opp = ev["opportunity"]
        status = "EXECUTE" if ev["decision"] == "EXECUTE" else "PENDING"
        
        # Create persistent decision record
        decision = await AgentDecision.create(
            vault=vault,
            agent=agent,
            status=status,
            opportunity_details={
                "pair_id": opp["pair_id"],
                "net_profit_usd": float(ev["net_profit_usd"]),
                "spread_pct": float(opp["spread_pct"]),
                "buy_pool": opp["buy_pool"],
                "sell_pool": opp["sell_pool"],
                "xtz_price": xtz_price,
                "gas_price_gwei": gas_price / 10**9
            }
        )
        
        if status == "EXECUTE":
            logger.info(f"🔔 NOTIFY: Decision {decision.id} ready for execution")
            # In a real environment with raw DB access, we'd do:
            # await ctx.execute_sql(f"NOTIFY agent_execute, '{decision.id}'")

    logger.info("═══════════════════════════════════════════════\n")
