import asyncio
import json
import sys
from pathlib import Path

from arbitrage_vault.utils import discover_pools
from arbitrage_vault.utils import get_xtz_price


async def main():
    print('Testing get_xtz_price...')
    price = await get_xtz_price()
    print(f'XTZ Price: {price}')

    print('\nTesting discover_pools and updating etherlink_pools.json...')
    pools = await discover_pools(max_pages=3)
    print(f'Found {len(pools)} pools.')

    # Resolve absolute path relative to this script: indexer/src/arbitrage_vault/tests/update_pools.py
    # target: contracts/test/etherlink_pools.json (5 levels up from filename)
    target_path = Path(__file__).resolve().parents[4] / 'contracts' / 'test' / 'etherlink_pools.json'

    target_path.write_text(json.dumps(pools, indent=2))

    print(f'Updated {target_path}')


if __name__ == '__main__':
    # Ensure we can import from the parent directory
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    asyncio.run(main())
