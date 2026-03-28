from tortoise import fields
from dipdup.models import Model

class ArbitrageVault(Model):
    address = fields.CharField(max_length=42, pk=True)
    name = fields.CharField(max_length=100)
    symbol = fields.CharField(max_length=20)
    asset_address = fields.CharField(max_length=42)
    created_at = fields.DatetimeField(auto_now_add=True)

class AgentDecision(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.ArbitrageVault', related_name='agent_decisions')
    decision = fields.CharField(max_length=10) # EXECUTE, SKIP
    reason = fields.TextField()
    opportunity_details = fields.JSONField()
    timestamp = fields.DatetimeField(auto_now_add=True)
    execution = fields.ForeignKeyField('models.ArbitrageExecution', related_name='agent_decisions', null=True)

class ArbitrageExecution(Model):
    id = fields.IntField(pk=True)
    agent = fields.ForeignKeyField('models.AgentDecision', related_name='executions')
    vault = fields.ForeignKeyField('models.ArbitrageVault', related_name='executions')
    strategist = fields.CharField(max_length=42)
    dex_buy = fields.ForeignKeyField('models.DexPool', related_name='buy_executions', null=True)
    dex_sell = fields.ForeignKeyField('models.DexPool', related_name='sell_executions', null=True)
    token_trade = fields.CharField(max_length=42)
    profit = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    transaction_hash = fields.CharField(max_length=66)

class DexPool(Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(max_length=42, unique=True)
    name = fields.CharField(max_length=100) # e.g. "oku-trade-etherlink"
    pair_name = fields.CharField(max_length=50) # e.g. "USDC/WXTZ"
    tvl_usd = fields.DecimalField(max_digits=36, decimal_places=2, default=0)
    tvl_xtz = fields.DecimalField(max_digits=36, decimal_places=18, default=0)
    last_updated = fields.DatetimeField(auto_now=True)

class VaultYield(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.ArbitrageVault', related_name='yields')
    profit = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    execution = fields.ForeignKeyField('models.ArbitrageExecution', related_name='yield_records', null=True)
    agent_decision = fields.ForeignKeyField('models.AgentDecision', related_name='yield_records', null=True)
    dex_pool = fields.ForeignKeyField('models.DexPool', related_name='yield_records', null=True)

class VaultSnapshot(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.ArbitrageVault', related_name='snapshots')
    total_assets = fields.DecimalField(max_digits=36, decimal_places=18)
    total_supply = fields.DecimalField(max_digits=36, decimal_places=18)
    yield_1d = fields.DecimalField(max_digits=36, decimal_places=18, null=True)
    yield_1w = fields.DecimalField(max_digits=36, decimal_places=18, null=True)
    yield_1m = fields.DecimalField(max_digits=36, decimal_places=18, null=True)
    apy = fields.DecimalField(max_digits=12, decimal_places=4, null=True)
    timestamp = fields.DatetimeField(auto_now_add=True)

class UserAction(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.ArbitrageVault', related_name='user_actions')
    user = fields.CharField(max_length=42)
    action_type = fields.CharField(max_length=10) # DEPOSIT, WITHDRAW
    assets = fields.DecimalField(max_digits=36, decimal_places=18)
    shares = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    transaction_hash = fields.CharField(max_length=66)
