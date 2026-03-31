from dipdup.models import Model
from tortoise import fields


class Vault(Model):
    address = fields.CharField(max_length=42, pk=True)
    name = fields.CharField(max_length=100)
    symbol = fields.CharField(max_length=20)
    asset_address = fields.CharField(max_length=42)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'vaults'


class VaultYield(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='yields')
    profit = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    execution = fields.ForeignKeyField('models.AgentExecution', related_name='yield_records', null=True)
    dex_pool = fields.ForeignKeyField('models.DexPool', related_name='yield_records', null=True)

    class Meta:
        table = 'vault_yields'


class VaultSnapshot(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='snapshots')
    total_assets = fields.DecimalField(max_digits=36, decimal_places=18)
    total_supply = fields.DecimalField(max_digits=36, decimal_places=18)
    yield_1d = fields.DecimalField(max_digits=36, decimal_places=18, null=True)
    yield_1w = fields.DecimalField(max_digits=36, decimal_places=18, null=True)
    yield_1m = fields.DecimalField(max_digits=36, decimal_places=18, null=True)
    apy = fields.DecimalField(max_digits=12, decimal_places=4, null=True)
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'vault_snapshots'


class UserAction(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='actions')
    user = fields.CharField(max_length=42, index=True)
    action_type = fields.CharField(max_length=10)  # DEPOSIT, WITHDRAW
    assets = fields.DecimalField(max_digits=36, decimal_places=18)
    shares = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    transaction_hash = fields.CharField(max_length=66, index=True)

    class Meta:
        table = 'user_actions'
