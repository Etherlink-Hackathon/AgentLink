/**
 * Price Extraction Module
 *
 * Takes discovered pools and organizes price data by token pair,
 * enabling cross-pool price comparison.
 */

import { logger } from "./logger.js";
import type { Pool, Token, TokenPairPrice } from "./types.js";

/**
 * Create a canonical pair ID from two token symbols (alphabetically sorted).
 * e.g. "USDC/WETH" regardless of which is token0/token1 in the pool.
 */
export function getPairId(symbolA: string, symbolB: string): string {
  return [symbolA, symbolB].sort().join("/");
}

/**
 * Extract and normalize prices from all pools.
 * Groups prices by canonical token pair for cross-pool comparison.
 */
export function extractPrices(
  pools: Pool[]
): Map<string, TokenPairPrice[]> {
  const priceMap = new Map<string, TokenPairPrice[]>();

  for (const pool of pools) {
    if (pool.price0 <= 0 || pool.price1 <= 0) {
      logger.debug(
        `Skipping pool ${pool.address} — invalid prices (${pool.price0}, ${pool.price1})`
      );
      continue;
    }

    const pairId = getPairId(pool.token0.symbol, pool.token1.symbol);

    // Determine canonical ordering (alphabetical)
    const [baseSymbol] = pairId.split("/");
    const isToken0Base = pool.token0.symbol === baseSymbol;

    const baseToken: Token = isToken0Base ? pool.token0 : pool.token1;
    const quoteToken: Token = isToken0Base ? pool.token1 : pool.token0;
    const price: number = isToken0Base ? pool.price0 : pool.price1;

    const entry: TokenPairPrice = {
      baseToken,
      quoteToken,
      price,
      pool,
    };

    const existing = priceMap.get(pairId);
    if (existing) {
      existing.push(entry);
    } else {
      priceMap.set(pairId, [entry]);
    }
  }

  logger.info(
    `Extracted prices for ${priceMap.size} token pairs across ${pools.length} pools`
  );

  // Log summary
  for (const [pairId, prices] of priceMap) {
    const priceRange = prices.map((p) => p.price);
    const min = Math.min(...priceRange);
    const max = Math.max(...priceRange);
    const spread = max > 0 ? ((max - min) / min) * 100 : 0;
    logger.debug(
      `${pairId}: ${prices.length} pools, price range ${min.toFixed(6)} - ${max.toFixed(6)} (${spread.toFixed(2)}% spread)`
    );
  }

  return priceMap;
}
