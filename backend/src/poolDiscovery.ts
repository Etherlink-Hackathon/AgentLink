/**
 * Pool Discovery Module
 *
 * Fetches liquidity pool data from the GeckoTerminal API for the Etherlink network.
 * Filters to supported token pairs and returns normalized Pool objects.
 */

import { logger } from "./logger.js";
import type {
  Pool,
  Token,
  GeckoPoolsResponse,
  GeckoPoolData,
  GeckoIncludedToken,
} from "./types.js";
import { SUPPORTED_TOKENS } from "./types.js";

const GECKO_API_BASE = "https://api.geckoterminal.com/api/v2";

/**
 * Fetch pools from GeckoTerminal for the given network.
 * Paginates through results and filters for supported tokens.
 */
export async function discoverPools(
  networkId: string,
  maxPages: number = 3
): Promise<Pool[]> {
  const allPools: Pool[] = [];

  for (let page = 1; page <= maxPages; page++) {
    const url = `${GECKO_API_BASE}/networks/${networkId}/pools?page=${page}&include=base_token,quote_token`;

    logger.debug(`Fetching pools page ${page}: ${url}`);

    try {
      const response = await fetch(url, {
        headers: {
          Accept: "application/json;version=20230302",
        },
      });

      if (!response.ok) {
        logger.warn(
          `GeckoTerminal API returned ${response.status} for page ${page}`
        );
        break;
      }

      const data = (await response.json()) as GeckoPoolsResponse;

      if (!data.data || data.data.length === 0) {
        logger.info(`No more pools found at page ${page}, stopping pagination`);
        break;
      }

      const tokenMap = buildTokenMap(data.included ?? []);
      const pools = parsePools(data.data, tokenMap);
      const filtered = filterSupportedPools(pools);

      allPools.push(...filtered);
      logger.info(
        `Page ${page}: found ${data.data.length} pools, ${filtered.length} with supported tokens`
      );

      // Respect rate limiting — brief pause between pages
      if (page < maxPages) {
        await sleep(1500);
      }
    } catch (error) {
      logger.error(`Failed to fetch pools page ${page}`, { error });
      break;
    }
  }

  logger.info(`Total pools discovered: ${allPools.length}`);
  return allPools;
}

/** Build a lookup map of token ID → Token from GeckoTerminal included data */
function buildTokenMap(included: GeckoIncludedToken[]): Map<string, Token> {
  const map = new Map<string, Token>();

  for (const item of included) {
    if (item.type === "token") {
      map.set(item.id, {
        address: item.attributes.address,
        symbol: item.attributes.symbol?.toUpperCase() ?? "UNKNOWN",
        name: item.attributes.name ?? "Unknown Token",
        decimals: item.attributes.decimals ?? 18,
      });
    }
  }

  return map;
}

/** Parse raw GeckoTerminal pool data into normalized Pool objects */
function parsePools(
  rawPools: GeckoPoolData[],
  tokenMap: Map<string, Token>
): Pool[] {
  const pools: Pool[] = [];

  for (const raw of rawPools) {
    try {
      const baseTokenId = raw.relationships.base_token.data.id;
      const quoteTokenId = raw.relationships.quote_token.data.id;
      const dexId = raw.relationships.dex.data.id;

      const token0 = tokenMap.get(baseTokenId);
      const token1 = tokenMap.get(quoteTokenId);

      if (!token0 || !token1) {
        continue; // skip pools with unresolved tokens
      }

      // Extract pool address from the GeckoTerminal ID (format: "network_address")
      const poolAddress = raw.attributes.address ?? raw.id.split("_").pop() ?? "";

      const basePrice = parseFloat(raw.attributes.base_token_price_usd || "0");
      const quotePrice = parseFloat(raw.attributes.quote_token_price_usd || "0");
      const tvl = parseFloat(raw.attributes.reserve_in_usd || "0");

      // Compute relative price: price of token0 in terms of token1
      const price0 = quotePrice > 0 ? basePrice / quotePrice : 0;
      const price1 = price0 > 0 ? 1 / price0 : 0;

      pools.push({
        address: poolAddress,
        dexName: dexId.replace(`${networkId}_`, "").replace(/_/g, " "),
        token0,
        token1,
        reserve0: 0n, // on-chain reserves fetched separately if needed
        reserve1: 0n,
        feeBps: 30, // default 0.3%; will be refined per DEX
        price0,
        price1,
        tvlUsd: tvl,
      });
    } catch (err) {
      logger.debug(`Skipping malformed pool entry: ${raw.id}`, { err });
    }
  }

  return pools;
}

// Variable captured in closure for parsePools — set by discoverPools caller context
let networkId = "etherlink";

/** Re-export for tests */
export function setNetworkId(id: string): void {
  networkId = id;
}

/** Filter pools to only those involving at least one supported token */
function filterSupportedPools(pools: Pool[]): Pool[] {
  const supported = new Set(SUPPORTED_TOKENS as readonly string[]);

  return pools.filter(
    (pool) =>
      supported.has(pool.token0.symbol) || supported.has(pool.token1.symbol)
  );
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
