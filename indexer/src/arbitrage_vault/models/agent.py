from dipdup.models import Model
from tortoise import fields


class Agent(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    address = fields.CharField(max_length=42, unique=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='agents')
    details = fields.JSONField()


class AgentDecision(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='decisions')
    agent = fields.ForeignKeyField('models.Agent', related_name='decisions')
    status = fields.CharField(max_length=20, default='PENDING', index=True)  # PENDING, EXECUTE, SENDING, SENT, FAILED
    heuristics_verdict = fields.CharField(max_length=10, null=True)  # APPROVE, REJECT
    gemini_verdict = fields.CharField(max_length=10, null=True)  # APPROVE, REJECT, TUNE
    opportunity_details = fields.JSONField()
    final_params = fields.JSONField(null=True)  # {max_gas, slippage_bps}
    tx_hash = fields.CharField(max_length=66, null=True, index=True)
    error = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    claimed_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'agent_decisions'


class AgentExecution(Model):
    id = fields.IntField(pk=True)
    agent = fields.ForeignKeyField('models.Agent', related_name='executions')
    vault = fields.ForeignKeyField('models.Vault', related_name='executions')
    # Link to the decision that triggered this execution
    decision = fields.ForeignKeyField('models.AgentDecision', related_name='executions', null=True)
    strategist = fields.CharField(max_length=42, index=True)

    # New Multi-hop field
    hops = fields.IntField(default=2)
    route_details = fields.JSONField(null=True)  # {tokens: [], pools: []}

    profit = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    transaction_hash = fields.CharField(max_length=66, index=True)

    class Meta:
        table = 'agent_executions'
