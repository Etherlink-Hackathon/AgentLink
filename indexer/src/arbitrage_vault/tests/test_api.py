import asyncio
import json
import logging

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GECKO_API_BASE = 'https://api.geckoterminal.com/api/v2'
WXTZ_ADDRESS = '0xc9B53AB2679f573e480d01e0f49e2d7838523EAb'


async def test_get_xtz_price():
    url = f'{GECKO_API_BASE}/simple/networks/etherlink/token_price/{WXTZ_ADDRESS}'
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0, headers={'Accept': 'application/json;version=20230302'})
            response.raise_for_status()
            data = response.json()
            print(f'XTZ Price Response: {json.dumps(data, indent=2)}')
            prices = data.get('data', {}).get('attributes', {}).get('token_prices', {})
            price = prices.get(WXTZ_ADDRESS.lower())
            print(f'XTZ Price: {price}')
        except Exception as e:
            print(f'Error fetching XTZ price: {e}')


async def test_discover_pools(network_id: str = 'etherlink'):
    async with httpx.AsyncClient() as client:
        url = f'{GECKO_API_BASE}/networks/{network_id}/pools?page=1&include=base_token,quote_token'
        try:
            response = await client.get(url, timeout=10.0, headers={'Accept': 'application/json;version=20230302'})
            response.raise_for_status()
            data = response.json()
            pools = data.get('data', [])
            for pool in pools[:3]:
                attrs = pool.get('attributes', {})
                print(f'Pool: {attrs.get("name")}')
                print(f'  base_token_price_usd: {attrs.get("base_token_price_usd")}')
                print(f'  quote_token_price_usd: {attrs.get("quote_token_price_usd")}')
                print(f'  base_token_price_native_token: {attrs.get("base_token_price_native_token")}')
                print(f'  quote_token_price_native_token: {attrs.get("quote_token_price_native_token")}')
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    print('Testing XTZ Price...')
    asyncio.run(test_get_xtz_price())
    print('\nTesting Discover Pools...')
    asyncio.run(test_discover_pools())
