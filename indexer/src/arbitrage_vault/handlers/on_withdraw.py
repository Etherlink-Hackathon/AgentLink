from arbitrage_vault.models import UserAction
from arbitrage_vault.models import Vault
from arbitrage_vault.types.ArbitrageVault.evm_events.withdraw import WithdrawPayload
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_withdraw(
    ctx: HandlerContext,
    event: EvmEvent[WithdrawPayload],
) -> None:
    vault, _ = await Vault.get_or_create(
        address=event.data.address,
        defaults={
            'name': 'Etherlink Arbitrage Vault',
            'symbol': 'EAV',
            'asset_address': '0x0000000000000000000000000000000000000000',
        },
    )

    assets = event.payload.assets / 10**18
    shares = event.payload.shares / 10**18

    await UserAction.create(
        vault=vault,
        user=event.payload.owner,
        action_type='WITHDRAW',
        assets=assets,
        shares=shares,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
    )
