from arbitrage_vault.models import ArbitrageExecution, ArbitrageVault, DexPool, VaultYield
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent
from arbitrage_vault.types.arbitrage_vault.evm_events.arbitrage_executed import ArbitrageExecuted


async def on_arbitrage_executed(
    ctx: HandlerContext,
    event: EvmEvent[ArbitrageExecuted],
) -> None:
    # 1. Get or create the Vault
    vault, _ = await ArbitrageVault.get_or_create(
        address=event.data.address,
        defaults={
            "name": "Etherlink Arbitrage Vault",
            "symbol": "EAV",
            "asset_address": "0x0000000000000000000000000000000000000000",
        }
    )

    # 2. Identify DEX Pools
    dex_buy, _ = await DexPool.get_or_create(
        address=event.payload.dexBuy,
        defaults={
            "name": "Buy DEX Router",
            "pair_name": f"Unknown/{event.payload.tokenTrade[:6]}",
        }
    )

    dex_sell, _ = await DexPool.get_or_create(
        address=event.payload.dexSell,
        defaults={
            "name": "Sell DEX Router",
            "pair_name": f"{event.payload.tokenTrade[:6]}/Unknown",
        }
    )

    profit = event.payload.profit / 10**18

    # 3. Create ArbitrageExecution
    execution = await ArbitrageExecution.create(
        vault=vault,
        strategist=event.payload.strategist,
        dex_buy=dex_buy,
        dex_sell=dex_sell,
        token_trade=event.payload.tokenTrade,
        profit=profit,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
        # agent=... # This will be linked by the agent service when it logs the decision
    )

    # 4. Record Yield
    await VaultYield.create(
        vault=vault,
        profit=profit,
        timestamp=event.data.timestamp,
        execution=execution,
        dex_pool=dex_buy, # Linking to buy pool as primary for this execution example
    )
