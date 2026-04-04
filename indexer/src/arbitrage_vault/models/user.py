from dipdup.models import Model
from tortoise import fields


class User(Model):
    """
    On-chain identity derived from UserAction events.
    Aggregated totals are updated on every deposit/withdraw.
    """

    address = fields.CharField(max_length=42, pk=True)
    total_deposited = fields.DecimalField(max_digits=36, decimal_places=18, default=0)
    total_withdrawn = fields.DecimalField(max_digits=36, decimal_places=18, default=0)
    # Current approximate shares held across all vaults
    total_shares = fields.DecimalField(max_digits=36, decimal_places=18, default=0)
    first_action_at = fields.DatetimeField(null=True)
    last_action_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'users'


class UserTVL(Model):
    """
    Time-series snapshot of a user's position in a specific vault.
    Inserted on every deposit/withdraw for charting TVL over time.
    """

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='tvl_history')
    vault = fields.ForeignKeyField('models.Vault', related_name='user_tvl_history')
    # Snapshot values at the moment of the action
    total_assets = fields.DecimalField(max_digits=36, decimal_places=18)
    shares = fields.DecimalField(max_digits=36, decimal_places=18)
    action_type = fields.CharField(max_length=10)  # DEPOSIT or WITHDRAW
    timestamp = fields.DatetimeField(index=True)

    class Meta:
        table = 'user_tvl'


class UserReward(Model):
    """
    A single reward credit attributed to a user from a specific AgentExecution.
    Reward is calculated as: execution.profit * (user_shares / vault_total_supply)
    at the time of the execution.
    """

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='rewards')
    vault = fields.ForeignKeyField('models.Vault', related_name='reward_records')
    execution = fields.ForeignKeyField('models.AgentExecution', related_name='execution_rewards')
    # User's proportional share of the vault at time of execution
    share_ratio = fields.DecimalField(max_digits=12, decimal_places=8)
    # Actual reward in asset units (profit * share_ratio)
    reward_assets = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField(index=True)

    class Meta:
        table = 'user_rewards'


class UserAction(Model):
    id = fields.IntField(pk=True)
    vault = fields.ForeignKeyField('models.Vault', related_name='actions')
    user = fields.CharField(max_length=42, index=True)
    # FK to the aggregated User profile (populated by the handler)
    user_profile = fields.ForeignKeyField('models.User', related_name='actions_history', null=True)
    action_type = fields.CharField(max_length=10)  # DEPOSIT, WITHDRAW
    assets = fields.DecimalField(max_digits=36, decimal_places=18)
    shares = fields.DecimalField(max_digits=36, decimal_places=18)
    timestamp = fields.DatetimeField()
    transaction_hash = fields.CharField(max_length=66, index=True)

    class Meta:
        table = 'user_actions'
