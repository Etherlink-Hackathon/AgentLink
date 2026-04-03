from arbitrage_vault.models import UserAction
from arbitrage_vault.models import Vault
from arbitrage_vault.types.ArbitrageVault.evm_events.deposit import DepositPayload
from arbitrage_vault.utils import DEFAULT_STRATEGIST
from arbitrage_vault.utils import ZERO_ADDRESS
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent


async def on_deposit(
    ctx: HandlerContext,
    event: EvmEvent[DepositPayload],
) -> None:
    vault, _ = await Vault.get_or_create(
        address=event.data.address,
        defaults={
            'name': 'Etherlink Arbitrage Vault',
            'symbol': 'EAV',
            'asset_address': ZERO_ADDRESS,
            'creator': event.payload.sender,
            'strategist': DEFAULT_STRATEGIST,
        },
    )

    assets = event.payload.assets / 10**18
    shares = event.payload.shares / 10**18

    await UserAction.create(
        vault=vault,
        user=event.payload.owner,
        action_type='DEPOSIT',
        assets=assets,
        shares=shares,
        timestamp=event.data.timestamp,
        transaction_hash=event.data.transaction_hash,
    )
