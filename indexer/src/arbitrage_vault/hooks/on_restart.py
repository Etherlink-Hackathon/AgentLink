"""Hook called on indexer restart."""

from dipdup.context import HookContext


async def on_restart(ctx: HookContext) -> None:
    """Called when the indexer restarts.

    This hook is called after the indexer has restarted and the database
    connection has been re-established.

    Args:
        ctx: Hook context
    """
    ctx.logger.info('Indexer restarted')

    # Initialize views
    await ctx.execute_sql('05-user-statistics')
    await ctx.execute_sql('06-user-reward-history')
    await ctx.execute_sql('07-vault-tvl-history')
