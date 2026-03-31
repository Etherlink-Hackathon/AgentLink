from arbitrage_vault.models import Agent
from arbitrage_vault.models import AgentExecution
from arbitrage_vault.models import DexPool
from arbitrage_vault.models import Token
from arbitrage_vault.models import Vault
from arbitrage_vault.models import VaultYield
from arbitrage_vault.types.ArbitrageVault.evm_events.multi_hop_arbitrage_executed import (
    MultiHopArbitrageExecutedPayload,
)
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_multi_hop_arbitrage_executed(
    ctx: HandlerContext,
    event: EvmEvent[MultiHopArbitrageExecutedPayload],
) -> None:
    # 1. Get or create the Vault
    vault, _ = await Vault.get_or_create(
        address=event.data.address,
        defaults={
            'name': 'Etherlink Arbitrage Vault',
            'symbol': 'EAV',
            'asset_address': '0x0000000000000000000000000000000000000000',
        },
    )

    # 2. Map or create the Agent (Soul)
    agent, _ = await Agent.get_or_create(
        address=event.payload.strategist,
        vault=vault,
        defaults={'name': 'Etherlink Soul Agent', 'details': {'role': 'STRATEGIST'}},
    )

    profit = event.payload.profit / 10**18

    # 3. Resolve human-readable details and build a step-by-step route
    steps_metadata = []
    for i in range(len(event.payload.pools)):
        # Resolve DEX name
        p_addr = event.payload.pools[i]
        p, _ = await DexPool.get_or_create(address=p_addr, defaults={'name': f'Dex {p_addr[:6]}'})

        # Resolve Token In symbol
        tin_addr = event.payload.route[i]
        tin, _ = await Token.get_or_create(address=tin_addr, defaults={'symbol': f'Token {tin_addr[:6]}'})

        # Resolve Token Out symbol
        tout_addr = event.payload.route[i + 1]
        tout, _ = await Token.get_or_create(address=tout_addr, defaults={'symbol': f'Token {tout_addr[:6]}'})

        steps_metadata.append({'dex': p.name, 'token_in': tin.symbol, 'token_out': tout.symbol, 'pool_address': p_addr})

    # 4. Create AgentExecution with a finalized 'steps' array for the UI
    execution = await AgentExecution.create(
        agent=agent,
        vault=vault,
        strategist=event.payload.strategist,
        hops=event.payload.hops,
        route_details={'steps': steps_metadata},
        profit=profit,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
    )

    # 5. Record yield for dashboard analytics
    await VaultYield.create(
        vault=vault,
        profit=profit,
        timestamp=event.data.timestamp,
        execution=execution,
    )
