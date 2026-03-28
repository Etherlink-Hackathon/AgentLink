import logging
import httpx
from typing import List, Dict, Any, Optional
from web3 import Web3

logger = logging.getLogger(__name__)

GECKO_API_BASE = "https://api.geckoterminal.com/api/v2"

async def get_xtz_price() -> float:
    """
    Fetch current XTZ price in USD via GeckoTerminal.
    """
    url = f"{GECKO_API_BASE}/networks/etherlink/pools/0x0000000000000000000000000000000000000000" # Placeholder for a deep liquidity pool
    # More robust: fetch from a known stable pair or the native token price endpoint
    url = "https://api.geckoterminal.com/api/v2/simple/networks/etherlink/token_price/0x0000000000000000000000000000000000000000" # WXTZ
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            # GeckoTerminal simple price returns { data: { id: ..., type: ..., attributes: { token_prices: { addr: price } } } }
            prices = data.get("data", {}).get("attributes", {}).get("token_prices", {})
            for addr, price in prices.items():
                return float(price)
        except Exception as e:
            logger.error(f"Error fetching XTZ price: {e}")
            return 1.5 # Fallback to a sane default

async def get_gas_price(rpc_url: str) -> int:
    """
    Fetch current gas price from the network.
    """
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3.eth.gas_price
    except Exception as e:
        logger.error(f"Error fetching gas price: {e}")
        return 1000000000 # 1 gwei fallback

async def discover_pools(network_id: str = "etherlink", max_pages: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch trending pools from GeckoTerminal API for the given network.
    """
    all_pools = []
    async with httpx.AsyncClient() as client:
        for page in range(1, max_pages + 1):
            url = f"{GECKO_API_BASE}/networks/{network_id}/pools?page={page}&include=base_token,quote_token"
            try:
                response = await client.get(url, timeout=10.0, headers={"Accept": "application/json;version=20230302"})
                response.raise_for_status()
                data = response.json()
                pools = data.get("data", [])
                if not pools:
                    break
                
                included = data.get("included", [])
                token_map = {item["id"]: item["attributes"] for item in included if item["type"] == "token"}
                
                for pool in pools:
                    try:
                        relationships = pool.get("relationships", {})
                        base_token_id = relationships.get("base_token", {}).get("data", {}).get("id")
                        quote_token_id = relationships.get("quote_token", {}).get("data", {}).get("id")
                        dex_id = relationships.get("dex", {}).get("data", {}).get("id", "unknown")
                        
                        token0 = token_map.get(base_token_id)
                        token1 = token_map.get(quote_token_id)
                        
                        if not token0 or not token1:
                            continue
                            
                        attributes = pool.get("attributes", {})
                        all_pools.append({
                            "address": attributes.get("address"),
                            "dex_name": dex_id.replace(f"{network_id}_", "").replace("_", " "),
                            "token0": token0,
                            "token1": token1,
                            "price0": float(attributes.get("base_token_price_usd") or 0) / float(attributes.get("quote_token_price_usd") or 1),
                            "tvl_usd": float(attributes.get("reserve_in_usd") or 0)
                        })
                    except Exception:
                        continue
                
                logger.info(f"Page {page}: found {len(pools)} pools")
            except Exception as e:
                logger.error(f"Error discovering pools at page {page}: {e}")
                break
                
    return all_pools

def get_pair_id(symbol_a: str, symbol_b: str) -> str:
    """Canonical pair ID."""
    return "/".join(sorted([symbol_a.upper(), symbol_b.upper()]))

def extract_prices(pools: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract and normalize prices from all pools.
    """
    price_map = {}
    for pool in pools:
        symbol0 = pool["token0"]["symbol"]
        symbol1 = pool["token1"]["symbol"]
        pair_id = get_pair_id(symbol0, symbol1)
        
        base_symbol = pair_id.split("/")[0]
        is_token0_base = symbol0.upper() == base_symbol
        
        price = pool["price0"] if is_token0_base else (1.0 / pool["price0"] if pool["price0"] > 0 else 0)
        
        if pair_id not in price_map:
            price_map[pair_id] = []
            
        price_map[pair_id].append({
            "base_token": pool["token0"] if is_token0_base else pool["token1"],
            "quote_token": pool["token1"] if is_token0_base else pool["token0"],
            "price": price,
            "pool": pool
        })
        
    return price_map
