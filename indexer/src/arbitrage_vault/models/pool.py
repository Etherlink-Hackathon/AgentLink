from dipdup.models import Model
from tortoise import fields


class DexPool(Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(max_length=42, unique=True, index=True)
    name = fields.CharField(max_length=100)  # e.g. "oku-trade-etherlink"
    token_a = fields.ForeignKeyField('models.Token', related_name='dex_pools_a')
    token_b = fields.ForeignKeyField('models.Token', related_name='dex_pools_b')
    tvl_usd = fields.DecimalField(max_digits=36, decimal_places=2, default=0)
    tvl_xtz = fields.DecimalField(max_digits=36, decimal_places=18, default=0)
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'dex_pools'
