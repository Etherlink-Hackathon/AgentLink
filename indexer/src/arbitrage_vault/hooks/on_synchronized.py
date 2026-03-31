import asyncio
import logging
import os

from arbitrage_vault.agent.gemini_soul import GeminiSoul
from arbitrage_vault.agent.strategy import ArbitrageHeuristics
from arbitrage_vault.models import AgentDecision
from dipdup.context import HookContext
from eth_account import Account
from web3 import Web3

logger = logging.getLogger(__name__)

# Set to store references to background tasks to prevent garbage collection (RUF006)
_background_tasks = set()


class AgentExecutor:
    _instance = None
    _semaphore = asyncio.Semaphore(1)

    def __init__(self, rpc_url: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.heuristics = ArbitrageHeuristics()
        self.soul = GeminiSoul()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            rpc_url = os.getenv('RPC_URL', 'https://node.mainnet.etherlink.com')
            pk = os.getenv('STRATEGIST_PRIVATE_KEY')
            if not pk:
                raise ValueError('STRATEGIST_PRIVATE_KEY is not set')
            cls._instance = cls(rpc_url, pk)
        return cls._instance

    async def process_decision(self, decision_id: int):
        """
        Main execution loop for a single decision.
        """
        async with self._semaphore:
            # 1. Lock and transition to SENDING
            decision = await AgentDecision.get_or_none(id=decision_id).select_for_update()
            if not decision or decision.status != 'EXECUTE':
                return

            decision.status = 'SENDING'
            await decision.save()

            try:
                # 2. Heuristics Check (Math)
                h_verdict = self.heuristics.evaluate(decision.opportunity_details)
                decision.heuristics_verdict = h_verdict['verdict']

                # 3. Gemini Soul Check (Context)
                g_verdict = await self.soul.review(decision.opportunity_details)
                if g_verdict:
                    decision.gemini_verdict = g_verdict['action']

                # 4. Decision logic (Math wins OR AI approves)
                if decision.heuristics_verdict == 'APPROVE' or (g_verdict and g_verdict['action'] == 'APPROVE'):
                    logger.info('🚀 Executing decision %s', decision_id)
                    tx_hash = await self._execute_on_chain(decision)
                    decision.tx_hash = tx_hash
                    decision.status = 'SENT'
                else:
                    decision.status = 'FAILED'
                    decision.error = f'Rejected: H={decision.heuristics_verdict}, G={decision.gemini_verdict}'

            except Exception as e:
                logger.error('Execution error %s: %s', decision_id, e)
                decision.status = 'FAILED'
                decision.error = str(e)

            await decision.save()

    async def _execute_on_chain(self, decision: AgentDecision) -> str:
        """
        Sign and broadcast the transaction.
        """
        # Placeholder for complex transaction building
        # In a real scenario, we'd use decision.opportunity_details to call vault.executeArbitrage
        # For now, we simulate a successful broadcast
        logger.info('Broadcasting transaction for decision %s...', decision.id)

        # Simplified example of sending a tx (e.g. transferring 0 ether to self)
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = {
            'nonce': nonce,
            'to': self.account.address,
            'value': 0,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,  # "Fast" strategy
            'chainId': 42793,
        }
        self.w3.eth.account.sign_transaction(tx, self.account.key)
        # tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        # return tx_hash.hex()

        return f'0x_simulated_hash_{decision.id}'


async def on_synchronized(ctx: HookContext):
    """
    Starts a long-running background task for LISTEN/NOTIFY or high-frequency polling.
    """
    executor = AgentExecutor.get_instance()

    async def _listener_loop():
        # Simple polling for now as DipDup doesn't expose raw asyncpg listener easily in hooks
        # In a full Postgres setup, we would use conn.add_listener
        logger.info('📡 Agent Executor Listener started in background')
        while True:
            try:
                # Check for EXECUTE status rows
                pending = await AgentDecision.filter(status='EXECUTE').all()
                for decision in pending:
                    await executor.process_decision(decision.id)

                await asyncio.sleep(1)  # Near-zero latency polling

            except Exception as e:
                logger.error('⚠️ Listener error: %s', e)
                await asyncio.sleep(1)

    # Start the loop in the background and let the hook finish
    task = asyncio.create_task(_listener_loop())

    # Add to set to prevent GC (RUF006)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    logger.info('✅ Hook on_synchronized completed, listener task handed over to background.')
