from arbitrage_vault.models import DexPool
from arbitrage_vault.types.ArbitrageVault.evm_events.dex_whitelisted import DexWhitelistedPayload
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_dex_whitelisted(
    ctx: HandlerContext,
    event: EvmEvent[DexWhitelistedPayload],
) -> None:
    # Get or create the DEX pool record
    # If it's a new pool, name will be generic until updated by a swap/discovery
    pool, _ = await DexPool.get_or_create(
        address=event.payload.dex,
        defaults={
            'name': f'DEX {event.payload.dex[:6]}',
            'is_whitelisted': event.payload.status,
        },
    )

    # Update whitelist status if it already exists
    if pool.is_whitelisted != event.payload.status:
        pool.is_whitelisted = event.payload.status
        await pool.save()
