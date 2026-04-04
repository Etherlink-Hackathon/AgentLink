from dipdup.context import HookContext


async def refresh_views(
    ctx: HookContext,
) -> None:
    """
    Refreshes all materialized views used by the arbitrage dashboard.
    Called by the 'refresh_views_scheduler' job.
    """
    await ctx.execute_sql('refresh_views')
