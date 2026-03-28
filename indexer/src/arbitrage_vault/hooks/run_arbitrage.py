import logging
import os
from typing import Any
from dipdup.context import HookContext
from arbitrage_vault.utils import discover_pools, extract_prices, get_xtz_price, get_gas_price
from arbitrage_vault.arbitrage import detect_arbitrage, evaluate_profitability
from arbitrage_vault.models import ArbitrageVault, AgentDecision

logger = logging.getLogger(__name__)

async def run_arbitrage(
    ctx: HookContext,
    vault_address: str,
    min_profit_usd: float = 0.1
) -> None:
    """
    Main hook to run an arbitrage cycle for a specific vault with dynamic cost analysis.
    """
    rpc_url = os.getenv("RPC_URL", "https://node.mainnet.etherlink.com")
    logger.info(f"🚀 Starting arbitrage cycle for vault {vault_address}")
    
    # 1. Fetch market and network context
    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)
    logger.info(f"📊 Market Context: XTZ=${xtz_price:.2f} | Gas={gas_price/10**9:.2f} gwei")
    
    # 2. Fetch Vault from DB
    vault = await ArbitrageVault.get_or_none(address=vault_address)
    if not vault:
        logger.error(f"Vault {vault_address} not found in database. Skipping cycle.")
        return

    # 3. Discover pools and extract prices
    pools = await discover_pools()
    if not pools:
        logger.warning("No pools discovered. Skipping cycle.")
        return
        
    price_map = extract_prices(pools)
    
    # 4. Detect and evaluate opportunities
    opportunities = detect_arbitrage(price_map)
    evaluations = await evaluate_profitability(
        opportunities, 
        xtz_price_usd=xtz_price,
        gas_price_wei=gas_price,
        min_profit_margin=0.005 # Refined default
    )
    
    # 5. Log decisions
    for ev in evaluations:
        opp = ev["opportunity"]
        
        # Log decision to DB for AI Agent "Soul" to process
        await AgentDecision.create(
            vault=vault,
            decision=ev["decision"],
            reason=ev["reason"],
            opportunity_details={
                "pair_id": opp["pair_id"],
                "spread_pct": float(opp["spread_pct"]),
                "buy_dex": opp["buy_pool"]["dex_name"],
                "sell_dex": opp["sell_pool"]["dex_name"],
                "net_profit_usd": float(ev["net_profit_usd"]),
                "xtz_price": xtz_price,
                "gas_price_gwei": gas_price / 10**9
            }
        )
        
        if ev["decision"] == "EXECUTE":
            logger.info(f"✅ EXECUTE: {opp['pair_id']} - Net profit: ${ev['net_profit_usd']:.4f}")
        else:
            logger.debug(f"⏭️ SKIP: {opp['pair_id']} - {ev['reason']}")

    logger.info("═══════════════════════════════════════════════\n")
