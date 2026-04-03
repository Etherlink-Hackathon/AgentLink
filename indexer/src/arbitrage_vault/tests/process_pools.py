import json


def process_data(page1_json, page2_json):
    network_id = 'etherlink'
    all_pools_data = []

    for page_json in [page1_json, page2_json]:
        data = json.loads(page_json)
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

    return all_pools_data


# The content of page 1 and 2 will be injected here during script generation
page1_content = """<PAGE1_JSON>"""
page2_content = """<PAGE2_JSON>"""

result = process_data(page1_content, page2_content)
print(json.dumps(result, indent=2))
