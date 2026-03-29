import logging
import os
import json
import asyncio
from typing import Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """
As a DeFi Arbitrage Strategist on Etherlink, evaluate this trading opportunity.
Respond ONLY in valid JSON.

OPPORTUNITY DATA:
{opp_json}

INVARIANTS:
- Chain ID: 42793 (Etherlink)
- Min Profit: $0.10
- Max Slippage: 0.5%

SCHEMA:
{{
  "action": "APPROVE | REJECT | TUNE",
  "reason": "short string",
  "confidence": 0.0-1.0,
  "params": {{
    "max_gas_gwei": number,
    "slippage_bps": number
  }}
}}
"""

class GeminiSoul:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3-flash')

    async def review(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call Gemini 1.5 Flash for a high-speed strategic review using the Google SDK.
        """
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. Skipping AI review.")
            return None

        prompt = PROMPT_TEMPLATE.format(opp_json=json.dumps(opportunity, indent=2))
        
        try:
            # Wrap the blocking generate_content call or use the async version
            # We enforce the 1s timeout as requested by the user
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                    )
                ),
                timeout=1.0
            )
            
            if response.text:
                return json.loads(response.text)
            return None
                
        except asyncio.TimeoutError:
            logger.warning("Gemini API review timed out after 1s. Falling back to heuristics.")
            return None
        except Exception as e:
            logger.error(f"Gemini SDK Error: {e}")
            return None
