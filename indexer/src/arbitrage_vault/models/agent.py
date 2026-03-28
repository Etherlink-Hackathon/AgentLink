from tortoise import fields
from dipdup.models import Model

class Agent(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    address = fields.CharField(max_length=42, unique=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='agents')
    details = fields.JSONField()
    
class AgentExecution(Model):
    id = fields.IntField(pk=True)
    agent = fields.ForeignKeyField('models.Agent', related_name='executions')
    vault = fields.ForeignKeyField('models.Vault', related_name='executions')
    strategist = fields.CharField(max_length=42, index=True)
    dex_buy = fields.ForeignKeyField('models.DexPool', related_name='buy_executions', null=True)
    dex_sell = fields.ForeignKeyField('models.DexPool', related_name='sell_executions', null=True)
    token_trade = fields.CharField(max_length=42)
    profit = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    transaction_hash = fields.CharField(max_length=66, index=True)

    class Meta:
        table = "agent_executions"
