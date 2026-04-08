import asyncio
import json
import logging
import os
import time
from pathlib import Path
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

# Cache for pool discovery to avoid rate limits
POOLS_CACHE_FILE = Path(__file__).parent / 'etherlink_pools.json'
POOLS_CACHE_TTL = 300  # 5 minutes

# ---------------------------------------------------------------------------
# Pool Provider Registry
# ---------------------------------------------------------------------------
# Each provider is a (dex_id, max_pages) tuple.
# To add a new DEX, simply append a new entry here — no code changes needed.
# dex_id must match GeckoTerminal's dex slug for the Etherlink network.
# Use `GET /networks/etherlink/dexes` to find valid IDs.

POOL_PROVIDERS: list[tuple[str, int]] = [
    ('oku-trade-etherlink', 10),
    ('curve-etherlink', 10),
]


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


async def get_price(token_address: str) -> float:
    """
    Fetch current USD price of any token on Etherlink via GeckoTerminal.
    Returns 0.0 if the price cannot be fetched.
    """
    url = f'{GECKO_API_BASE}/simple/networks/etherlink/token_price/{token_address.lower()}'
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0, headers={'Accept': 'application/json;version=20230302'})
            if response.status_code == 200:
                data = response.json()
                prices = data.get('data', {}).get('attributes', {}).get('token_prices', {})
                price = prices.get(token_address.lower())
                if price:
                    return float(price)
        except Exception as e:
            logger.error('Error fetching price for %s: %s', token_address, e)
    return 0.0


async def get_prices(token_addresses: list[str]) -> dict[str, float]:
    """
    Batch fetch USD prices for multiple tokens on Etherlink via GeckoTerminal.
    GeckoTerminal supports comma-separated addresses in the token_price endpoint.
    Returns a dict of {lowercase_address: price_usd}.
    """
    if not token_addresses:
        return {}
    # Batch in groups of 30 to stay well within URL length limits
    results: dict[str, float] = {}
    async with httpx.AsyncClient() as client:
        chunk_size = 30
        for i in range(0, len(token_addresses), chunk_size):
            chunk = token_addresses[i : i + chunk_size]
            addresses_str = ','.join(addr.lower() for addr in chunk)
            url = f'{GECKO_API_BASE}/simple/networks/etherlink/token_price/{addresses_str}'
            try:
                response = await client.get(url, timeout=15.0, headers={'Accept': 'application/json;version=20230302'})
                if response.status_code == 200:
                    data = response.json()
                    prices = data.get('data', {}).get('attributes', {}).get('token_prices', {})
                    for addr, price in prices.items():
                        if price:
                            results[addr.lower()] = float(price)
            except Exception as e:
                logger.error('Error batch fetching prices for chunk: %s', e)
            if i + chunk_size < len(token_addresses):
                await asyncio.sleep(0.5)  # brief pause between chunks
    return results


async def get_xtz_price() -> float:
    """
    Fetch current XTZ/WXTZ price in USD.
    Thin wrapper around get_price for backwards compatibility.
    """
    wxtz_address = '0xc9b53ab2679f573e480d01e0f49e2b5cfb7a3eab'
    price = await get_price(wxtz_address)
    return price if price > 0 else 0.34


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


# ---------------------------------------------------------------------------
# Per-DEX Pool Fetcher
# ---------------------------------------------------------------------------


async def _fetch_dex_pools(
    client: httpx.AsyncClient,
    dex_id: str,
    max_pages: int = 10,
    network_id: str = 'etherlink',
) -> list[dict[str, Any]]:
    """
    Fetch ALL pools for a specific DEX using the per-DEX endpoint.
    Uses /networks/{network}/dexes/{dex}/pools which returns all pools,
    not just trending ones.
    """
    pools: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        if page > 1:
            await asyncio.sleep(2.0)  # Respect rate limits

        url = f'{GECKO_API_BASE}/networks/{network_id}/dexes/{dex_id}/pools?page={page}&include=base_token,quote_token'
        try:
            response = await client.get(url, timeout=15.0, headers={'Accept': 'application/json;version=20230302'})

            if response.status_code == 429:
                logger.warning('⚠️ Rate limited (429) fetching %s page %d. Backing off...', dex_id, page)
                await asyncio.sleep(5.0)
                # Retry once after backoff
                response = await client.get(url, timeout=15.0, headers={'Accept': 'application/json;version=20230302'})
                if response.status_code == 429:
                    logger.warning('⚠️ Still rate limited. Stopping %s at page %d.', dex_id, page)
                    break

            response.raise_for_status()
            data = response.json()
            raw_pools = data.get('data', [])
            if not raw_pools:
                logger.info('📄 %s: No more pools at page %d', dex_id, page)
                break

            included = data.get('included', [])
            token_map = {item['id']: item['attributes'] for item in included if item['type'] == 'token'}

            page_count = 0
            for pool in raw_pools:
                try:
                    attributes = pool.get('attributes', {})
                    relationships = pool.get('relationships', {})

                    base_token_id = relationships.get('base_token', {}).get('data', {}).get('id')
                    quote_token_id = relationships.get('quote_token', {}).get('data', {}).get('id')

                    if not base_token_id or not quote_token_id:
                        continue
                    if base_token_id not in token_map or quote_token_id not in token_map:
                        continue

                    base_price = float(attributes.get('base_token_price_usd') or 0)
                    quote_price = float(attributes.get('quote_token_price_usd') or 1)

                    pools.append(
                        {
                            'address': Web3.to_checksum_address(attributes['address']),
                            'dex_name': dex_id,
                            'token0': token_map[base_token_id],
                            'token1': token_map[quote_token_id],
                            'price0': base_price / quote_price if quote_price > 0 else 0,
                            'tvl_usd': float(attributes.get('reserve_in_usd') or 0),
                            'fee': float(attributes.get('swap_fee_pct') or 0.3),
                        }
                    )
                    page_count += 1
                except Exception as e:
                    logger.error('Failed to parse pool from %s: %s', dex_id, e)
                    continue

            logger.info('📄 %s page %d: imported %d pools', dex_id, page, page_count)

        except httpx.HTTPStatusError as e:
            logger.error('HTTP error fetching %s page %d: %s', dex_id, page, e)
            break
        except Exception as e:
            logger.error('Error fetching %s page %d: %s', dex_id, page, e)
            continue

    return pools


async def discover_pools(
    network_id: str = 'etherlink',
    max_pages: int = 10,
    force_refresh: bool = False,
    providers: list[tuple[str, int]] | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch ALL pools from each registered DEX provider.

    Uses the per-DEX endpoint /networks/{network}/dexes/{dex}/pools
    to get comprehensive coverage instead of just trending pools.

    Args:
        network_id: GeckoTerminal network slug.
        max_pages: Default max pages per provider (overridden by provider config).
        force_refresh: Skip cache and fetch fresh data.
        providers: Custom provider list; defaults to POOL_PROVIDERS.
    """
    active_providers = providers or POOL_PROVIDERS

    # 1. Try Cache First (unless forcing refresh)
    if POOLS_CACHE_FILE.exists() and not force_refresh:
        age = time.time() - POOLS_CACHE_FILE.stat().st_mtime
        if age < POOLS_CACHE_TTL:
            try:
                if POOLS_CACHE_FILE.stat().st_size == 0:
                    raise json.JSONDecodeError('Empty file', '', 0)
                with POOLS_CACHE_FILE.open() as f:
                    cached_pools = json.load(f)
                    logger.info('📡 Using cached pools (%d pools, age: %ds)', len(cached_pools), int(age))
                    return cached_pools
            except (json.JSONDecodeError, Exception) as e:
                logger.warning('Cache invalid or empty, fetching fresh: %s', e)

    # 2. Fetch from ALL providers
    all_pools: list[dict[str, Any]] = []
    seen_addresses: set[str] = set()  # Deduplicate by pool address

    async with httpx.AsyncClient() as client:
        for dex_id, dex_max_pages in active_providers:
            logger.info('🔍 Fetching pools from %s (up to %d pages)...', dex_id, dex_max_pages)
            dex_pools = await _fetch_dex_pools(client, dex_id, max_pages=dex_max_pages, network_id=network_id)

            new_count = 0
            for pool in dex_pools:
                addr_key = pool['address'].lower()
                if addr_key not in seen_addresses:
                    seen_addresses.add(addr_key)
                    all_pools.append(pool)
                    new_count += 1

            logger.info(
                '✅ %s: %d pools fetched, %d new (after dedup)',
                dex_id,
                len(dex_pools),
                new_count,
            )

            # Pause between providers to respect rate limits
            await asyncio.sleep(2.0)

    logger.info('📊 Total unique pools discovered: %d from %d providers', len(all_pools), len(active_providers))

    # 3. Enrich tokens with live USD prices
    if all_pools:
        unique_tokens: list[str] = list(
            {
                addr
                for pool in all_pools
                for addr in [pool['token0']['address'].lower(), pool['token1']['address'].lower()]
            }
        )
        logger.info('💰 Fetching live USD prices for %d unique tokens...', len(unique_tokens))
        token_prices = await get_prices(unique_tokens)
        enriched = 0
        for pool in all_pools:
            t0_addr = pool['token0']['address'].lower()
            t1_addr = pool['token1']['address'].lower()
            p0 = token_prices.get(t0_addr, 0.0)
            p1 = token_prices.get(t1_addr, 0.0)
            pool['token0']['price_usd'] = p0
            pool['token1']['price_usd'] = p1
            if p0 > 0:
                enriched += 1
            if p1 > 0:
                enriched += 1
        logger.info('💰 Enriched %d token slots with price_usd (total %d tokens)', enriched, len(unique_tokens))

    # 4. Update Cache & Return
    if all_pools:
        try:
            with POOLS_CACHE_FILE.open('w') as f:
                json.dump(all_pools, f, indent=2)
                logger.info('💾 Cache updated: %d pools saved to %s', len(all_pools), POOLS_CACHE_FILE.name)
            return all_pools
        except Exception as e:
            logger.error('Failed to save pools cache: %s', e)

    # 5. Final Fallback to Stale Cache
    if POOLS_CACHE_FILE.exists():
        try:
            with POOLS_CACHE_FILE.open() as f:
                cached_pools = json.load(f)
                logger.info('📡 Falling back to stale cache (%d pools)', len(cached_pools))
                return cached_pools
        except Exception:
            pass

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
