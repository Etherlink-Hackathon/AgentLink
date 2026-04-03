from arbitrage_vault.models import Vault
from arbitrage_vault.types.ArbitrageVault.evm_events.role_granted import RoleGrantedPayload
from arbitrage_vault.utils import ZERO_ADDRESS
from dipdup.context import HandlerContext
from dipdup.models.evm import EvmEvent

DEFAULT_ADMIN_ROLE = '0x0000000000000000000000000000000000000000000000000000000000000000'


async def on_role_granted(
    ctx: HandlerContext,
    event: EvmEvent[RoleGrantedPayload],
) -> None:
    # 1. Convert role bytes to hex string for comparison
    role_hex = '0x' + event.payload.role.hex()

    # 2. Get or create the Vault
    vault, _ = await Vault.get_or_create(
        address=event.data.address,
        defaults={
            'name': 'Etherlink Arbitrage Vault',
            'symbol': 'EAV',
            'asset_address': ZERO_ADDRESS,
            'creator': event.payload.sender,
            'strategist': event.payload.account,
        },
    )

    # 3. If this is the admin role, then account is the definitive creator
    if role_hex == DEFAULT_ADMIN_ROLE:
        vault.creator = event.payload.account
        await vault.save()
