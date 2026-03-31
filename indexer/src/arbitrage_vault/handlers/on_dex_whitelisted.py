from arbitrage_vault.models import DexPool
from arbitrage_vault.models import Token
from arbitrage_vault.types.ArbitrageVault.evm_events.dex_whitelisted import DexWhitelistedPayload
from arbitrage_vault.utils import fetch_pool_metadata
from arbitrage_vault.utils import fetch_token_metadata
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_dex_whitelisted(
    ctx: HandlerContext,
    event: EvmEvent[DexWhitelistedPayload],
) -> None:
    # Resolve a better name immediately if possible
    p_addr = event.payload.dex.lower()
    name_fallback = f'DEX {p_addr[:6]}'

    # Get or create the DEX pool record
    pool, created = await DexPool.get_or_create(
        address=p_addr,
        defaults={
            'name': name_fallback,
            'is_whitelisted': event.payload.status,
        },
    )

    # If new or has placeholder name, try to enrich
    if created or pool.name == name_fallback or pool.name.startswith(('DEX 0x', 'Pool 0x')):
        meta = await fetch_pool_metadata(p_addr)

        # 1. Update Name
        if meta['name'] != pool.name:
            pool.name = meta['name']

        # 2. Extract and link Token A
        if meta['token0']:
            t0_addr = meta['token0'].lower()
            t0, _ = await Token.get_or_create(
                address=t0_addr,
                defaults={'name': f'Token {t0_addr[:8]}', 'symbol': f'TKN_{t0_addr[:6]}', 'decimals': 18},
            )
            if _ or t0.name.startswith('Token '):
                t0_meta = await fetch_token_metadata(t0_addr)
                if t0_meta['name']:
                    t0.name = t0_meta['name']
                    t0.symbol = (t0_meta['symbol'] or t0.symbol)[:20]
                    t0.decimals = t0_meta['decimals'] or t0.decimals
                    await t0.save()
            pool.token_a = t0

        # 3. Extract and link Token B
        if meta['token1']:
            t1_addr = meta['token1'].lower()
            t1, _ = await Token.get_or_create(
                address=t1_addr,
                defaults={'name': f'Token {t1_addr[:8]}', 'symbol': f'TKN_{t1_addr[:6]}', 'decimals': 18},
            )
            if _ or t1.name.startswith('Token '):
                t1_meta = await fetch_token_metadata(t1_addr)
                if t1_meta['name']:
                    t1.name = t1_meta['name']
                    t1.symbol = (t1_meta['symbol'] or t1.symbol)[:20]
                    t1.decimals = t1_meta['decimals'] or t1.decimals
                    await t1.save()
            pool.token_b = t1

        await pool.save()

    # Update whitelist status if it changed
    if pool.is_whitelisted != event.payload.status:
        pool.is_whitelisted = event.payload.status
        await pool.save()
