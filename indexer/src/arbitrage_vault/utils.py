import asyncio
import logging
import os
from typing import Any

import httpx
from web3 import Web3

_ERC20_ABI = [
    {'inputs': [], 'name': 'name', 'outputs': [{'type': 'string'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'symbol', 'outputs': [{'type': 'string'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'decimals', 'outputs': [{'type': 'uint8'}], 'stateMutability': 'view', 'type': 'function'},
]

logger = logging.getLogger(__name__)

GECKO_API_BASE = 'https://api.geckoterminal.com/api/v2'
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
DEFAULT_STRATEGIST = '0x0000000000000000000000000000000000000000'


def _get_w3() -> Web3:
    rpc_url = os.environ.get('RPC_URL', 'https://node.mainnet.etherlink.com')
    return Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))


def _fetch_token_metadata_sync(address: str) -> dict[str, Any]:
    """Synchronous ERC-20 metadata fetch. Runs in a thread executor."""
    w3 = _get_w3()
    checksum = w3.to_checksum_address(address)
    contract = w3.eth.contract(address=checksum, abi=_ERC20_ABI)
    result: dict[str, Any] = {}
    for field in ('name', 'symbol', 'decimals'):
        try:
            result[field] = contract.functions[field]().call()
        except Exception as exc:
            logger.debug('on-chain %s() failed for %s: %s', field, address, exc)
            result[field] = None
    return result


async def fetch_token_metadata(address: str) -> dict[str, Any]:
    """
    Fetch ERC-20 name / symbol / decimals from the chain.
    Returns a dict with keys 'name', 'symbol', 'decimals'.
    Any field that fails the RPC call is returned as None.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_token_metadata_sync, address)


_POOL_METADATA_ABI = [
    {'inputs': [], 'name': 'name', 'outputs': [{'type': 'string'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'symbol', 'outputs': [{'type': 'string'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'token0', 'outputs': [{'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'token1', 'outputs': [{'type': 'address'}], 'stateMutability': 'view', 'type': 'function'},
    {'inputs': [], 'name': 'fee', 'outputs': [{'type': 'uint24'}], 'stateMutability': 'view', 'type': 'function'},
    {
        'inputs': [{'type': 'uint256'}],
        'name': 'coins',
        'outputs': [{'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
]


def _fetch_pool_metadata_sync(pool_address: str) -> dict[str, Any]:
    """Try on-chain calls for name, symbol, token0, token1, fee."""
    w3 = _get_w3()
    checksum = w3.to_checksum_address(pool_address)
    contract = w3.eth.contract(address=checksum, abi=_POOL_METADATA_ABI)
    result = {'name': None, 'symbol': None, 'token0': None, 'token1': None, 'fee': None}

    for field in ('name', 'symbol', 'token0', 'token1', 'fee'):
        try:
            result[field] = contract.functions[field]().call()
        except Exception:
            pass

    # Fallback for Curve coins(0)/coins(1)
    if not result['token0']:
        try:
            result['token0'] = contract.functions.coins(0).call()
            result['token1'] = contract.functions.coins(1).call()
        except Exception:
            pass

    return result


async def fetch_pool_metadata(pool_address: str) -> dict[str, Any]:
    """
    Resolve a human-readable name and token addresses for a DEX pool.
    Returns: {'name': str, 'token0': str|None, 'token1': str|None}
    """
    res = {'name': None, 'token0': None, 'token1': None}

    # --- 1. GeckoTerminal ---
    url = f'{GECKO_API_BASE}/networks/etherlink/pools/{pool_address.lower()}?include=dex'
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, headers={'Accept': 'application/json;version=20230302'})
            if resp.status_code == 200:
                data = resp.json()
                attrs = data.get('data', {}).get('attributes', {})
                pool_label: str | None = attrs.get('name')

                rel = data.get('data', {}).get('relationships', {})
                t0_id = rel.get('base_token', {}).get('data', {}).get('id', '')
                t1_id = rel.get('quote_token', {}).get('data', {}).get('id', '')
                if t0_id.startswith('etherlink_'):
                    res['token0'] = t0_id.split('_')[1]
                if t1_id.startswith('etherlink_'):
                    res['token1'] = t1_id.split('_')[1]

                dex_name = None
                included = data.get('included', [])
                for item in included:
                    if item.get('type') == 'dex':
                        dex_name = item.get('attributes', {}).get('name')
                        break

                if not dex_name:
                    dex_id = rel.get('dex', {}).get('data', {}).get('id', '')
                    dex_name = dex_id.replace('etherlink', '').replace('-', ' ').replace('_', ' ').strip().title()

                if pool_label:
                    res['name'] = f'{dex_name} — {pool_label}' if dex_name else pool_label
                    return res
    except Exception as exc:
        logger.debug('GeckoTerminal metadata lookup failed: %s', exc)

    # --- 2. on-chain fallbacks ---
    loop = asyncio.get_event_loop()
    on_chain = await loop.run_in_executor(None, _fetch_pool_metadata_sync, pool_address)
    res['token0'] = on_chain['token0'] or res['token0']
    res['token1'] = on_chain['token1'] or res['token1']

    # Try to construct a name if missing
    name = on_chain['name'] or on_chain['symbol']
    if not name and res['token0'] and res['token1']:
        # Fetch token symbols for a better fallback
        t0_meta = await fetch_token_metadata(res['token0'])
        t1_meta = await fetch_token_metadata(res['token1'])
        t0_sym = t0_meta['symbol'] or res['token0'][:6]
        t1_sym = t1_meta['symbol'] or res['token1'][:6]

        fee_suffix = ''
        if on_chain['fee'] is not None:
            # fee is in hundredths of a basis point (e.g. 3000 = 0.3%)
            fee_suffix = f' — {on_chain["fee"] / 10000}%'

        name = f'Uniswap V3 — {t0_sym}/{t1_sym}{fee_suffix}' if on_chain['fee'] else f'{t0_sym}/{t1_sym}'

    res['name'] = name or f'Pool {pool_address[:8]}'
    return res


async def get_xtz_price() -> float:
    """
    Fetch current XTZ price in USD via GeckoTerminal.
    Uses WXTZ (0xc9b53ab2679f573e480d01e0f49e2d7838523eab) as a proxy for XTZ.
    """
    wxtz_address = '0xc9b53ab2679f573e480d01e0f49e2d7838523eab'
    url = f'{GECKO_API_BASE}/simple/networks/etherlink/token_price/{wxtz_address}'
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0, headers={'Accept': 'application/json;version=20230302'})
            if response.status_code == 200:
                data = response.json()
                prices = data.get('data', {}).get('attributes', {}).get('token_prices', {})
                price = prices.get(wxtz_address)
                if price:
                    return float(price)

            # Fallback: discover trending pools and find WXTZ
            pools = await discover_pools(max_pages=1)
            for pool in pools:
                if pool['token0']['address'].lower() == wxtz_address:
                    return float(pool['token0'].get('price_usd') or 0)
                if pool['token1']['address'].lower() == wxtz_address:
                    return float(pool['token1'].get('price_usd') or 0)

            return 0.34  # Current sane default if all else fails
        except Exception as e:
            logger.error('Error fetching XTZ price: %s', e)
            return 0.34


async def get_gas_price(rpc_url: str) -> int:
    """
    Fetch current gas price from the network.
    """
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3.eth.gas_price
    except Exception as e:
        logger.error('Error fetching gas price: %s', e)
        return 1000000000  # 1 gwei fallback


async def discover_pools(network_id: str = 'etherlink', max_pages: int = 3) -> list[dict[str, Any]]:
    """
    Fetch trending pools from GeckoTerminal API for the given network.
    """
    all_pools = []
    async with httpx.AsyncClient() as client:
        for page in range(1, max_pages + 1):
            url = f'{GECKO_API_BASE}/networks/{network_id}/pools?page={page}&include=base_token,quote_token'
            try:
                response = await client.get(url, timeout=10.0, headers={'Accept': 'application/json;version=20230302'})
                response.raise_for_status()
                data = response.json()
                pools = data.get('data', [])
                if not pools:
                    break

                included = data.get('included', [])
                token_map = {item['id']: item['attributes'] for item in included if item['type'] == 'token'}

                for pool in pools:
                    try:
                        relationships = pool.get('relationships', {})
                        base_token_id = relationships.get('base_token', {}).get('data', {}).get('id')
                        quote_token_id = relationships.get('quote_token', {}).get('data', {}).get('id')
                        dex_id = relationships.get('dex', {}).get('data', {}).get('id', 'unknown')

                        token0 = token_map.get(base_token_id)
                        token1 = token_map.get(quote_token_id)

                        if not token0 or not token1:
                            continue

                        attributes = pool.get('attributes', {})
                        all_pools.append(
                            {
                                'address': attributes.get('address'),
                                'dex_name': dex_id.replace(f'{network_id}_', '').replace('_', ' '),
                                'token0': token0,
                                'token1': token1,
                                'price0': float(attributes.get('base_token_price_usd') or 0)
                                / float(attributes.get('quote_token_price_usd') or 1),
                                'tvl_usd': float(attributes.get('reserve_in_usd') or 0),
                            }
                        )
                    except Exception:
                        continue

                logger.info('Page %s: found %s pools', page, len(pools))
            except Exception as e:
                logger.error('Error discovering pools at page %s: %s', page, e)
                break

    return all_pools


def get_pair_id(symbol_a: str, symbol_b: str) -> str:
    """Canonical pair ID."""
    return '/'.join(sorted([symbol_a.upper(), symbol_b.upper()]))


def extract_prices(pools: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Extract and normalize prices from all pools.
    """
    price_map = {}
    for pool in pools:
        symbol0 = pool['token0']['symbol']
        symbol1 = pool['token1']['symbol']
        pair_id = get_pair_id(symbol0, symbol1)

        base_symbol = pair_id.split('/')[0]
        is_token0_base = symbol0.upper() == base_symbol

        price = pool['price0'] if is_token0_base else (1.0 / pool['price0'] if pool['price0'] > 0 else 0)

        if pair_id not in price_map:
            price_map[pair_id] = []

        price_map[pair_id].append(
            {
                'base_token': pool['token0'] if is_token0_base else pool['token1'],
                'quote_token': pool['token1'] if is_token0_base else pool['token0'],
                'price': price,
                'pool': pool,
            }
        )

    return price_map
