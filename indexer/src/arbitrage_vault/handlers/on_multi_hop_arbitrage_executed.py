from arbitrage_vault.models import Agent
from arbitrage_vault.models import AgentExecution
from arbitrage_vault.models import DexPool
from arbitrage_vault.models import Token
from arbitrage_vault.models import Vault
from arbitrage_vault.models import VaultYield
from arbitrage_vault.types.ArbitrageVault.evm_events.multi_hop_arbitrage_executed import (
    MultiHopArbitrageExecutedPayload,
)
from arbitrage_vault.utils import ZERO_ADDRESS
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_multi_hop_arbitrage_executed(
    ctx: HandlerContext,
    event: EvmEvent[MultiHopArbitrageExecutedPayload],
) -> None:
    # 1. Get or create the Vault
    vault_addr = event.data.address.lower()
    vault, _ = await Vault.get_or_create(
        address=vault_addr,
        defaults={
            'name': 'Etherlink Arbitrage Vault',
            'symbol': 'EAV',
            'asset_address': ZERO_ADDRESS,
            'creator': event.payload.strategist,
            'strategist': event.payload.strategist,
        },
    )

    # 2. Map or create the Agent (Soul)
    agent_addr = event.payload.strategist.lower()
    agent, _ = await Agent.get_or_create(
        address=agent_addr,
        vault=vault,
        defaults={'name': 'Etherlink Soul Agent', 'details': {'role': 'STRATEGIST'}},
    )

    import eth_abi
    from arbitrage_vault.utils import fetch_pool_metadata
    from arbitrage_vault.utils import fetch_token_metadata

    # 3. Decode the raw data (route, pools, hops, profit) from the log
    # MultiHopArbitrageExecuted(address indexed strategist, address[] route, address[] pools, uint256 hops, uint256 profit)
    decoded = eth_abi.decode(['address[]', 'address[]', 'uint256', 'uint256'], bytes.fromhex(event.data.data[2:]))
    route = list(decoded[0])
    pools = list(decoded[1])
    hops = int(decoded[2])
    raw_profit = int(decoded[3])

    # Dynamic scaling based on vault asset decimals
    asset_addr = vault.asset_address.lower()
    asset_tokens = None
    if asset_addr != ZERO_ADDRESS:
        asset_tokens, _ = await Token.get_or_create(
            address=asset_addr,
            defaults={'name': 'Vault Asset', 'symbol': 'ASSET', 'decimals': 18},
        )
        # If it's a first see or placeholder name, enrich!
        if _ or asset_tokens.name == 'Vault Asset':
            meta = await fetch_token_metadata(asset_addr)
            if meta and meta['decimals'] is not None:
                asset_tokens.name = meta.get('name') or asset_tokens.name
                asset_tokens.symbol = meta.get('symbol') or asset_tokens.symbol
                asset_tokens.decimals = meta.get('decimals') or asset_tokens.decimals
                await asset_tokens.save()

    decimals = asset_tokens.decimals if asset_tokens else 18
    profit = float(raw_profit) / (10**decimals)

    # 4. Resolve human-readable details and build a step-by-step route
    steps_metadata = []
    for i in range(len(pools)):
        # ── DEX Pool ────────────────────────────────────────────────────────
        p_addr = pools[i].lower()
        p, p_created = await DexPool.get_or_create(
            address=p_addr,
            defaults={'name': f'Pool {p_addr[:8]}'},
        )
        if p_created or p.name.startswith(('Pool ', 'DEX ')):
            meta = await fetch_pool_metadata(p_addr)
            if meta['name'] != p.name:
                p.name = meta['name']

            # Bridge Token A
            if meta['token0'] and not p.token_a:
                t0_addr = meta['token0'].lower()
                if t0_addr != ZERO_ADDRESS:
                    p.token_a, _ = await Token.get_or_create(
                        address=t0_addr,
                        defaults={'name': f'Token {t0_addr[:8]}', 'symbol': f'TKN_{t0_addr[:6]}', 'decimals': 18},
                    )
            # Bridge Token B
            if meta['token1'] and not p.token_b:
                t1_addr = meta['token1'].lower()
                if t1_addr != ZERO_ADDRESS:
                    p.token_b, _ = await Token.get_or_create(
                        address=t1_addr,
                        defaults={'name': f'Token {t1_addr[:8]}', 'symbol': f'TKN_{t1_addr[:6]}', 'decimals': 18},
                    )
            await p.save()

        # ── Token In ────────────────────────────────────────────────────────
        tin_addr = route[i].lower()
        tin = None
        if tin_addr != ZERO_ADDRESS:
            tin, tin_created = await Token.get_or_create(
                address=tin_addr,
                defaults={'name': f'Token {tin_addr[:8]}', 'symbol': f'TKN_{tin_addr[:6]}', 'decimals': 18},
            )
            if tin_created:
                meta = await fetch_token_metadata(tin_addr)
                tin.name = meta.get('name') or tin.name
                tin.symbol = (meta.get('symbol') or tin.symbol)[:20]  # field max_length=20
                tin.decimals = meta.get('decimals') or tin.decimals
                await tin.save(update_fields=['name', 'symbol', 'decimals'])

        # ── Token Out ───────────────────────────────────────────────────────
        tout_addr = route[i + 1].lower()
        tout = None
        if tout_addr != ZERO_ADDRESS:
            tout, tout_created = await Token.get_or_create(
                address=tout_addr,
                defaults={'name': f'Token {tout_addr[:8]}', 'symbol': f'TKN_{tout_addr[:6]}', 'decimals': 18},
            )
            if tout_created:
                meta = await fetch_token_metadata(tout_addr)
                tout.name = meta.get('name') or tout.name
                tout.symbol = (meta.get('symbol') or tout.symbol)[:20]
                tout.decimals = meta.get('decimals') or tout.decimals
                await tout.save(update_fields=['name', 'symbol', 'decimals'])

        steps_metadata.append(
            {
                'dex': p.name,
                'token_in': tin.symbol if tin else 'XTZ',
                'token_out': tout.symbol if tout else 'XTZ',
                'pool_address': p_addr,
            }
        )

    # 5. Create AgentExecution with a finalized 'steps' array for the UI
    execution = await AgentExecution.create(
        agent=agent,
        vault=vault,
        strategist=event.payload.strategist,
        hops=hops,
        route_details={'steps': steps_metadata},
        profit=profit,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
    )

    # 6. Record yield for dashboard analytics
    # Associate the yield with the first pool in the route for visibility
    first_pool_addr = pools[0].lower()
    first_pool = await DexPool.get(address=first_pool_addr)
    await VaultYield.create(
        vault=vault,
        profit=profit,
        timestamp=event.data.timestamp,
        execution=execution,
        dex_pool=first_pool,
    )
