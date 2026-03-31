import asyncio
import json
import logging
import os
from typing import Any

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
- Min Profit Floor: $0.10
- Max Slippage: 0.5% (50 bps)

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
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            # New SDK uses Client object
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-2.0-flash'

    async def review(
        self, opportunity: dict[str, Any], strategy_config: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        Call Gemini for a high-speed strategic review using the Google SDK.
        """
        if not self.api_key:
            logger.warning('GEMINI_API_KEY not set. Skipping AI review.')
            return None

        opp_data = {'opportunity': opportunity, 'agent_strategy': strategy_config or {}}

        prompt = PROMPT_TEMPLATE.format(opp_json=json.dumps(opp_data, indent=2))

        try:
            # Use the new async client syntax (aio)
            response = await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                    ),
                ),
                timeout=1.2,  # Slightly more buffer for the new client
            )

            if response.text:
                return json.loads(response.text)
            return None

        except TimeoutError:
            logger.warning('Gemini API review timed out after 1.2s. Falling back to heuristics.')
            return None
        except Exception as e:
            logger.error('Gemini SDK Error: %s', e)
            return None

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
