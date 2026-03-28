from arbitrage_vault.models import UserAction, ArbitrageVault
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent
from arbitrage_vault.types.arbitrage_vault.evm_events.withdraw import Withdraw


async def on_withdraw(
    ctx: HandlerContext,
    event: EvmEvent[Withdraw],
) -> None:
    vault, _ = await ArbitrageVault.get_or_create(
        address=event.data.address,
        defaults={
            "name": "Etherlink Arbitrage Vault",
            "symbol": "EAV",
            "asset_address": "0x0000000000000000000000000000000000000000",
        }
    )

    assets = event.payload.assets / 10**18
    shares = event.payload.shares / 10**18

    await UserAction.create(
        vault=vault,
        user=event.payload.owner,
        action_type="WITHDRAW",
        assets=assets,
        shares=shares,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
    )
