from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

from arbitrage_vault.agent.gemini_soul import GeminiSoul
from arbitrage_vault.agent.strategy import ArbitrageHeuristics
from arbitrage_vault.models import AgentDecision
from eth_account import Account
from web3 import Web3

if TYPE_CHECKING:
    from dipdup.context import HookContext

logger = logging.getLogger(__name__)

# Set to store references to background tasks to prevent garbage collection (RUF006)
_background_tasks = set()


class AgentExecutor:
    _instance: ClassVar[AgentExecutor | None] = None
    _semaphore: ClassVar[asyncio.Semaphore] = asyncio.Semaphore(1)

    DEX_TYPE_MAP: ClassVar[dict[str, int]] = {
        'uniswap v2': 0,
        'uniswap v3': 1,
        'camelot v3': 1,
        'pancakeswap v3': 1,
        'curve': 2,
        'universal router': 3,
    }

    def __init__(self, rpc_url: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.heuristics = ArbitrageHeuristics()
        self.soul = GeminiSoul()

        # Load Vault ABI
        abi_path = Path(__file__).parent.parent / 'abi' / 'ArbitrageVault' / 'abi.json'
        with abi_path.open() as f:
            self.vault_abi = json.load(f)

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
                # 2. Load Agent Config
                agent = await decision.agent
                config = agent.strategy_config or {}

                # 3. Heuristics Check (Math)
                h_verdict = self.heuristics.evaluate(decision.opportunity_details, strategy_config=config)
                decision.heuristics_verdict = h_verdict['verdict']

                # 4. Gemini Soul Check (Context)
                g_verdict = await self.soul.review(decision.opportunity_details, strategy_config=config)
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
        opp = decision.opportunity_details
        vault_address = (await decision.vault).address
        vault_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(vault_address), abi=self.vault_abi)

        # 1. Construct Steps
        # A standard arbitrage: Asset -> Buy Token X -> Sell for Asset
        # For simplicity, we assume the vault asset is the base token of the pair (or quote)

        buy_pool = opp['buy_pool']
        sell_pool = opp['sell_pool']

        # Determine tokens
        # GeckoTerminal uses standard addresses. We need to be sure which one is 'tokenIn'
        # For now, we assume a simple 2-hop: Vault Asset -> Token X -> Vault Asset
        # In a real environment, we'd resolve this from the Vault's .asset() call
        vault_asset = vault_contract.functions.asset().call()

        # Determine the intermediate token (Token X)
        t0 = self.w3.to_checksum_address(buy_pool['token0']['address'])
        t1 = self.w3.to_checksum_address(buy_pool['token1']['address'])
        token_x = t1 if t0.lower() == vault_asset.lower() else t0

        steps = [
            {
                'dex': self.w3.to_checksum_address(buy_pool['address']),
                'dexType': self.DEX_TYPE_MAP.get(buy_pool.get('dex_name', '').lower(), 1),  # Default to V3 if unknown
                'tokenIn': vault_asset,
                'tokenOut': token_x,
                'data': b'',  # Use default pathing in contract
            },
            {
                'dex': self.w3.to_checksum_address(sell_pool['address']),
                'dexType': self.DEX_TYPE_MAP.get(sell_pool.get('dex_name', '').lower(), 1),
                'tokenIn': token_x,
                'tokenOut': vault_asset,
                'data': b'',
            },
        ]

        # 2. Params
        amount_in = 10**18  # 1 unit default for testing or use a percentage of vault balance
        # In a production agent, we'd fetch the actual vault balance
        try:
            amount_in = vault_contract.functions.totalAssets().call()
            # Use only 10% for safety in tests if not specified
            amount_in = amount_in // 10
        except Exception:
            pass

        min_profit = int(
            opp.get('net_profit_usd', 0) * 10**18 / opp.get('xtz_price', 1.5)
        )  # Rough conversion to native
        if min_profit < 0:
            min_profit = 0

        # 3. Build Tx
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price

        # High-performance: Add 10% premium to gas to ensure inclusion
        fast_gas_price = int(gas_price * 1.1)

        tx = vault_contract.functions.executeMultiHop(steps, amount_in, min_profit).build_transaction(
            {
                'from': self.account.address,
                'nonce': nonce,
                'gas': 1_200_000,  # Conservative estimate for multi-hop
                'gasPrice': fast_gas_price,
                'chainId': 42793,
            }
        )

        # 4. Sign and Send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)

        if os.getenv('DRY_RUN') == 'true':
            logger.info('DRY RUN: Transaction signed, skipping broadcast. Decision %s', decision.id)
            return f'0x_dry_run_hash_{decision.id}'

        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info('🔔 Arbitrage transaction sent: %s', tx_hash.hex())

        return tx_hash.hex()


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
