from dipdup.models import Model
from tortoise import fields


class Token(Model):
    id = fields.IntField(pk=True)
    address = fields.CharField(max_length=42, unique=True, index=True)
    name = fields.CharField(max_length=100)
    symbol = fields.CharField(max_length=20, index=True)
    decimals = fields.IntField()

    class Meta:
        table = 'tokens'
