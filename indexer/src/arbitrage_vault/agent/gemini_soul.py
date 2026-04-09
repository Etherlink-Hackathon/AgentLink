import asyncio
import json
import logging
import os
from typing import Any
from typing import ClassVar

from eth_abi import encode as abi_encode
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
As a DeFi Arbitrage Strategist on Etherlink, evaluate this trading opportunity.
Respond ONLY in valid JSON.

OPPORTUNITY DATA:
{opp_json}

INVARIANTS:
- Chain ID: 42793 (Etherlink)
- DexType Mapping: UNISWAP_V2:0, UNISWAP_V3:1, CURVE:2, UNIVERSAL_ROUTER:3, CURVE_V2:4
- Min Profit Floor: ${min_profit_usd:.4f}
- Max Slippage: {max_slippage_pct:.2f}% ({max_slippage_bps} bps)
- Interval: 5 minutes

SECURITY:
- You MUST define 'min_expected_profit_usd' to prevent sandwich attacks.
- For UNIVERSAL_ROUTER (3), ensure 'payerIsUser' is false.

SCHEMA:
{{
  "action": "APPROVE | REJECT | TUNE",
  "reason": "short string",
  "confidence": 0.0-1.0,
  "params": {{
    "max_gas_gwei": number,
    "slippage_bps": number,
    "min_expected_profit_usd": number
  }}
}}
"""


class GeminiSoul:
    # Ranked model list for fallbacks exactly as requested
    FALLBACK_MODELS: ClassVar[list[str]] = [
        'gemini-2.5-flash-lite',
        'gemini-3.1-pro',
        'gemini-3.1-flash-lite',
        'gemini-2-flash-lite',
        'gemini-2-flash',
        'gemini-2.5-pro',
        'gemini-2.5-flash',
        'gemini-3-flash',
    ]

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.model_index = 0
        self.model_id = self.FALLBACK_MODELS[0]

        if self.api_key:
            # Configure client with automatic retries for basic network issues
            self.client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(attempts=3, initial_delay=2.0, http_status_codes=[500, 503])
                ),
            )

    async def review(
        self, opportunity: dict[str, Any], strategy_config: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Call Gemini for a high-speed strategic review using the Google SDK.
        """
        if not self.api_key:
            logger.warning('GEMINI_API_KEY not set. Skipping AI review.')
            return None

        # Check for mock mode for rapid testing
        if os.getenv('MOCK_AI_REVIEW') == 'true' or os.getenv('DRY_RUN') == 'true':
            logger.info('🛡️ MOCK AI: Simulating approval for %s (DRY_RUN mode)', opportunity['pair_id'])
            return {
                'action': 'APPROVE',
                'reason': 'Simulated approval for testing',
                'confidence': 0.95,
                'params': {'max_gas_gwei': 50, 'slippage_bps': 50, 'min_expected_profit_usd': 0.01},
            }

        opp_data = {'opportunity': opportunity, 'agent_strategy': strategy_config or {}}

        # Extract values for prompt formatting
        config = strategy_config or {}
        min_profit_usd = config.get('min_profit_usd', 0.001)
        max_slippage_bps = config.get('max_slippage_bps', 50)
        max_slippage_pct = max_slippage_bps / 100.0

        prompt = PROMPT_TEMPLATE.format(
            opp_json=json.dumps(opp_data, indent=2),
            min_profit_usd=min_profit_usd,
            max_slippage_bps=max_slippage_bps,
            max_slippage_pct=max_slippage_pct,
        )

        for _attempt in range(len(self.FALLBACK_MODELS) * 2):
            try:
                # Use the new async client syntax (aio)
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model_id,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type='application/json',
                            temperature=0.1,
                        ),
                    ),
                    timeout=12.0,
                )

                if response.text:
                    return json.loads(response.text)
                return None

            except TimeoutError:
                logger.warning('Gemini API review timed out for %s. Attempting next model...', self.model_id)
                self._rotate_model()
                await asyncio.sleep(1)
            except Exception as e:
                err_str = str(e)

                # Check for model-specific failures (404/429)
                if any(x in err_str for x in ['404', '429', 'RESOURCE_EXHAUSTED', 'NOT_FOUND', 'PermissionDenied']):
                    logger.warning('Model %s failed: %s. Falling back...', self.model_id, err_str[:50])
                    self._rotate_model()
                    await asyncio.sleep(2)
                    continue

                logger.error('Gemini SDK Error: %s', e)
                return None

        return None

    def _rotate_model(self):
        """Switch to the next model in the fallback list."""
        self.model_index = (self.model_index + 1) % len(self.FALLBACK_MODELS)
        self.model_id = self.FALLBACK_MODELS[self.model_index]
        logger.info('🔄 Switched to model: %s', self.model_id)

    @staticmethod
    def encode_universal_router_swap(
        recipient: str, amount_in: int, amount_out_min: int, path: bytes, payer_is_user: bool = False
    ) -> str:
        """
        Python equivalent of the Universal Router V3_SWAP_EXACT_IN encoder.
        Used by the AI Strategist to build secure payloads for the ArbitrageVault.
        """
        # Command 0x00 = V3_SWAP_EXACT_IN
        commands = b'\x00'

        # Input: (address recipient, uint256 amountIn, uint256 amountOutMin, bytes path, bool payerIsUser)
        input_data = abi_encode(
            ['address', 'uint256', 'uint256', 'bytes', 'bool'],
            [recipient, amount_in, amount_out_min, path, payer_is_user],
        )

        # Final dexData: (bytes commands, bytes[] inputs)
        # Note: In Python/eth-abi, bytes[] is encoded as [input_data]
        encoded_payload = abi_encode(['bytes', 'bytes[]'], [commands, [input_data]])

        return '0x' + encoded_payload.hex()
