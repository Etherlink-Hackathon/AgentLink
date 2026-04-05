from datetime import UTC
from datetime import datetime
from decimal import Decimal

from arbitrage_vault.models import User
from arbitrage_vault.models import UserAction
from arbitrage_vault.models import UserTVL
from arbitrage_vault.models import Vault
from arbitrage_vault.types.ArbitrageVault.evm_events.withdraw import WithdrawPayload
from arbitrage_vault.utils import DEFAULT_STRATEGIST
from arbitrage_vault.utils import ZERO_ADDRESS
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
            'asset_address': ZERO_ADDRESS,
            'creator': event.payload.sender,
            'strategist': DEFAULT_STRATEGIST,
        },
    )

    assets = Decimal(event.payload.assets) / Decimal(10**18)
    shares = Decimal(event.payload.shares) / Decimal(10**18)
    owner = event.payload.owner.lower()
    timestamp = datetime.fromtimestamp(event.data.timestamp, tz=UTC)

    # 1. Get or create the User profile
    user, created = await User.get_or_create(
        address=owner,
        defaults={
            'total_withdrawn': assets,
            # Shares reduce on withdrawal; clamp to 0 to avoid negative
            'total_shares': Decimal(0),
            'first_action_at': timestamp,
            'last_action_at': timestamp,
        },
    )

    if not created:
        user.total_withdrawn += assets
        user.total_shares = max(Decimal(0), user.total_shares - shares)
        user.last_action_at = timestamp
        if user.first_action_at is None:
            user.first_action_at = timestamp
        await user.save(update_fields=['total_withdrawn', 'total_shares', 'last_action_at', 'first_action_at'])

    # 2. Record the action
    await UserAction.create(
        vault=vault,
        user=owner,
        user_profile=user,
        action_type='WITHDRAW',
        assets=assets,
        shares=shares,
        timestamp=timestamp,
        transaction_hash=event.data.transaction_hash,
    )

    # 3. Insert a UserTVL snapshot for charting
    await UserTVL.create(
        user=user,
        vault=vault,
        total_assets=max(Decimal(0), user.total_deposited - user.total_withdrawn),
        shares=user.total_shares,
        action_type='WITHDRAW',
        timestamp=timestamp,
    )
