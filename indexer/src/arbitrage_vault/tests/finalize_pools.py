import json
from pathlib import Path


def process_pool_json(file_path):
    with Path(file_path).open(encoding='utf-8') as f:
        content = f.read()
        # Skip header: Source: ... \n\n --- \n\n
        try:
            json_str = content.split('---', 1)[1].strip()
            return json.loads(json_str)
        except (IndexError, json.JSONDecodeError) as e:
            print(f'Error processing {file_path}: {e}')
            return None


def main():
    network_id = 'etherlink'
    all_pools_data = []

    # Paths to the fetched content files
    base_dir = Path(
        r'C:\Users\ASUS\.gemini\antigravity\brain\867192dc-8731-4cd5-b05b-4850481ccdba\.system_generated\steps'
    )
    files = [base_dir / '71' / 'content.md', base_dir / '77' / 'content.md']

    for file_path in files:
        data = process_pool_json(file_path)
        if not data:
            continue

        pools = data.get('data', [])
        included = data.get('included', [])
        token_map = {item['id']: item['attributes'] for item in included if item['type'] == 'token'}

        for pool in pools:
            relationships = pool.get('relationships', {})
            base_token_id = relationships.get('base_token', {}).get('data', {}).get('id')
            quote_token_id = relationships.get('quote_token', {}).get('data', {}).get('id')
            dex_id = relationships.get('dex', {}).get('data', {}).get('id', 'unknown')

            token0 = token_map.get(base_token_id)
            token1 = token_map.get(quote_token_id)

            if not token0 or not token1:
                continue

            attributes = pool.get('attributes', {})
            base_price = float(attributes.get('base_token_price_usd') or 0)
            quote_price = float(attributes.get('quote_token_price_usd') or 1)

            all_pools_data.append(
                {
                    'address': attributes.get('address'),
                    'dex_name': dex_id.replace(f'{network_id}_', '').replace('_', ' '),
                    'token0': token0,
                    'token1': token1,
                    'price0': base_price / quote_price if quote_price != 0 else 0,
                    'tvl_usd': float(attributes.get('reserve_in_usd') or 0),
                }
            )

    # Write to the final target file
    target_path = Path(r'f:\EtherlinkDex\contracts\test\etherlink_pools.json')
    with target_path.open('w', encoding='utf-8') as f:
        json.dump(all_pools_data, f, indent=2)

    print(f'Successfully processed {len(all_pools_data)} pools and updated {target_path}')


if __name__ == '__main__':
    main()
