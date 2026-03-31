from arbitrage_vault.models import Agent
from arbitrage_vault.models import AgentExecution
from arbitrage_vault.models import DexPool
from arbitrage_vault.models import Token
from arbitrage_vault.models import Vault
from arbitrage_vault.models import VaultYield
from arbitrage_vault.types.ArbitrageVault.evm_events.arbitrage_executed import ArbitrageExecutedPayload
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_arbitrage_executed(
    ctx: HandlerContext,
    event: EvmEvent[ArbitrageExecutedPayload],
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

    # 2. Identify tokens (Generic placeholders)
    asset_token, _ = await Token.get_or_create(
        address=vault.asset_address, defaults={'name': 'Vault Asset', 'symbol': 'ASSET', 'decimals': 18}
    )
    trade_token, _ = await Token.get_or_create(
        address=event.payload.tokenTrade, defaults={'name': 'Trade Token', 'symbol': 'TRADE', 'decimals': 18}
    )

    # 3. Identify DexPools
    dex_buy, _ = await DexPool.get_or_create(
        address=event.payload.dexBuy,
        defaults={
            'name': f'Buy DEX ({event.payload.dexBuy[:6]})',
            'token_a': asset_token,
            'token_b': trade_token,
        },
    )
    dex_sell, _ = await DexPool.get_or_create(
        address=event.payload.dexSell,
        defaults={
            'name': f'Sell DEX ({event.payload.dexSell[:6]})',
            'token_a': trade_token,
            'token_b': asset_token,
        },
    )

    # 4. Map or create the Agent (Soul)
    # The strategist address comes from the on-chain event
    agent, _ = await Agent.get_or_create(
        address=event.payload.strategist,
        vault=vault,
        defaults={'name': 'Etherlink Soul Agent', 'details': {'role': 'STRATEGIST'}},
    )

    profit = event.payload.profit / 10**18

    # 5. Create AgentExecution
    execution = await AgentExecution.create(
        agent=agent,
        vault=vault,
        strategist=event.payload.strategist,
        dex_buy=dex_buy,
        dex_sell=dex_sell,
        token_trade=event.payload.tokenTrade,
        profit=profit,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
    )

    # 6. Record yield
    await VaultYield.create(
        vault=vault,
        profit=profit,
        timestamp=event.data.timestamp,
        execution=execution,
        dex_pool=dex_buy,
    )
