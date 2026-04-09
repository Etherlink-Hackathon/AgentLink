import logging
import os
from typing import Any

from arbitrage_vault.agent.arbitrage import detect_multi_hop_arbitrage
from arbitrage_vault.agent.arbitrage import evaluate_profitability
from arbitrage_vault.models import Agent
from arbitrage_vault.models import AgentDecision
from arbitrage_vault.models import Vault
from arbitrage_vault.utils import discover_pools
from arbitrage_vault.utils import get_gas_price
from arbitrage_vault.utils import get_xtz_price
from dipdup.context import HookContext

logger = logging.getLogger(__name__)


async def run_arbitrage(
    ctx: HookContext,
    vault_address: str,
    min_profit_usd: float = 0.001,
    opportunities: list[dict[str, Any]] | None = None,
) -> None:
    """
    Main hook to run an arbitrage cycle for a specific vault.
    Now inserts AgentDecision records for async processing.
    """
    rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')
    strategist_address = os.getenv('STRATEGIST_ADDRESS', '0x0000000000000000000000000000000000000000')

    logger.info('🚀 Starting arbitrage cycle for vault %s', vault_address)

    xtz_price = await get_xtz_price()
    gas_price = await get_gas_price(rpc_url)

    vault = await Vault.get_or_none(address=vault_address)
    if not vault:
        logger.error('Vault %s not found. Skipping.', vault_address)
        return

    # 1. Fetch/Create Agent to get strategy configuration
    DEFAULT_STRATEGY = {
        'min_profit_usd': min_profit_usd,
        'allowed_pools': [],  # [] means all allowed
        'max_slippage_bps': 50,
        'refresh_interval': 180,
    }

    agent, _ = await Agent.get_or_create(
        address=strategist_address,
        vault=vault,
        defaults={
            'name': 'Etherlink Soul Agent',
            'details': {'role': 'STRATEGIST'},
            'strategy_config': DEFAULT_STRATEGY,
        },
    )

    # Auto-initialize existing records that have NULL config
    if agent.strategy_config is None:
        agent.strategy_config = DEFAULT_STRATEGY
        await agent.save()

    # 2. Discover and filter opportunities
    if opportunities is None:
        pools = await discover_pools(force_refresh=True)
        if not pools:
            return

        # Filter pools based on strategy config
        if agent.strategy_config and agent.strategy_config.get('allowed_pools'):
            allowed = [addr.lower() for addr in agent.strategy_config['allowed_pools']]
            pools = [p for p in pools if p['address'].lower() in allowed]
            logger.info('Filtered to %s allowed pools for agent %s', len(pools), agent.name)

        if not pools:
            logger.warning('No allowed pools found for scanning.')
            return

        opportunities = detect_multi_hop_arbitrage(pools, asset_token_address=getattr(vault, 'asset_address', None))
    else:
        logger.info('Using %d externally provided opportunities', len(opportunities))

    evaluations = await evaluate_profitability(
        opportunities, xtz_price_usd=xtz_price, gas_price_wei=gas_price, min_profit_margin=0.001
    )

    from arbitrage_vault.agent.gemini_soul import GeminiSoul
    from arbitrage_vault.agent.strategy import ArbitrageHeuristics

    ai_soul = GeminiSoul()
    heuristics = ArbitrageHeuristics()

    for ev in evaluations:
        opp = ev['opportunity']

        # Multi-hop SCOUT: log but don't skip recording
        if ev['decision'] == 'SCOUT':
            logger.info(
                '🔭 SCOUT route (%d hops, +%.2f%%): %s',
                opp.get('hops', '?'),
                opp.get('return_pct', 0) * 100,
                opp['pair_id'],
            )

        # Combine base profitability with strategic heuristics
        h_verdict = heuristics.evaluate(
            {**opp, 'net_profit_usd': ev['net_profit_usd']}, strategy_config=agent.strategy_config
        )

        heuristics_passed = ev['decision'] == 'EXECUTE' and h_verdict['verdict'] == 'APPROVE'

        # Determine status: EXECUTE if heuristics/AI pass or if FORCE_EXECUTION is set
        force_exec = os.getenv('FORCE_EXECUTION') == 'true'
        status = 'EXECUTE' if (heuristics_passed or force_exec) else ev['decision']

        if force_exec and status != 'EXECUTE':
            status = 'EXECUTE'
            logger.warning(
                '⚠️ FORCE_EXECUTION enabled: marking %s as EXECUTE regardless of profitability', opp['pair_id']
            )

        # 3. AI Review (if heuristics approve)
        ai_review = None
        if heuristics_passed:
            logger.info(
                '🤖 Heuristics passed for %s (+%.2f) - Requesting AI Review...', opp['pair_id'], ev['net_profit_usd']
            )
            ai_review = await ai_soul.review(opp, strategy_config=agent.strategy_config)

            if ai_review:
                action = ai_review.get('action', 'REJECT')
                confidence = ai_review.get('confidence', 0.0)
                reason = ai_review.get('reason', 'No reason given')

                if action == 'REJECT':
                    status = 'PENDING'  # AI veto
                    logger.warning('❌ AI VETO for %s: %s (Confidence: %.1f)', opp['pair_id'], reason, confidence)
                else:
                    status = 'EXECUTE'
                    logger.info('✅ AI APPROVAL: %s (Confidence: %.1f)', reason, confidence)
            else:
                status = 'PENDING'  # Fallback to pending if AI review fails
                logger.warning('⚠️ AI Review failed for %s. Skipping for safety.', opp['pair_id'])

        # Create persistent decision record
        decision = await AgentDecision.create(
            vault=vault,
            agent=agent,
            status=status,
            heuristics_verdict='APPROVE' if heuristics_passed else 'REJECT',
            gemini_verdict=ai_review.get('action') if ai_review else None,
            confidence=ai_review.get('confidence') if ai_review else None,
            reason=ai_review.get('reason') if ai_review else ev.get('reason'),
            opportunity_details={
                'pair_id': opp['pair_id'],
                'route': opp.get('route'),
                'net_profit_usd': float(ev['net_profit_usd']),
                'return_pct': float(opp.get('return_pct', opp.get('spread_pct', 0))),
                'hops': opp.get('hops', 2),
                'is_direct': opp.get('is_direct', True),
                'buy_pool': opp.get('buy_pool'),
                'sell_pool': opp.get('sell_pool'),
                'xtz_price': xtz_price,
                'gas_price_gwei': gas_price / 10**9,
                'ai_params': ai_review.get('params') if ai_review else None,
            },
        )

        if status == 'EXECUTE':
            logger.info('🔔 NOTIFY: Decision %s ready for execution', decision.id)
            # In a real environment with raw DB access, we'd do:
            # await ctx.execute_sql(f"NOTIFY agent_execute, '{decision.id}'")

    logger.info('═══════════════════════════════════════════════\n')
