/**
 * Arbitrage Detection Module
 *
 * Compares prices across pools for the same token pair
 * and identifies spread opportunities.
 */

import { logger } from "./logger.js";
import type { ArbitrageOpportunity, TokenPairPrice } from "./types.js";

/**
 * Detect arbitrage opportunities from price data.
 *
 * For each token pair with prices from multiple pools,
 * compare every pair of pools and identify spreads above minSpread.
 *
 * @param priceMap - Map of pairId → prices from extractPrices()
 * @param minSpreadPct - Minimum spread percentage to consider (e.g. 0.005 = 0.5%)
 * @returns Array of detected opportunities, sorted by spread descending
 */
export function detectArbitrage(
  priceMap: Map<string, TokenPairPrice[]>,
  minSpreadPct: number = 0
): ArbitrageOpportunity[] {
  const opportunities: ArbitrageOpportunity[] = [];

  for (const [pairId, prices] of priceMap) {
    // Need at least 2 pools to compare
    if (prices.length < 2) {
      continue;
    }

    // Compare every pair of pools
    for (let i = 0; i < prices.length; i++) {
      for (let j = i + 1; j < prices.length; j++) {
        const a = prices[i];
        const b = prices[j];

        // Determine which is cheaper (buy) and which is more expensive (sell)
        const [buy, sell] =
          a.price < b.price ? [a, b] : [b, a];

        const spread = (sell.price - buy.price) / buy.price;

        if (spread <= minSpreadPct) {
          continue;
        }

        // Estimate gross profit based on the smaller pool's TVL
        // Use 1% of the smaller pool's TVL as a conservative trade size
        const tradeSize =
          Math.min(buy.pool.tvlUsd, sell.pool.tvlUsd) * 0.01;
        const grossProfit = tradeSize * spread;

        const opportunity: ArbitrageOpportunity = {
          pairId,
          baseToken: buy.baseToken,
          quoteToken: buy.quoteToken,
          buyPool: buy.pool,
          buyPrice: buy.price,
          sellPool: sell.pool,
          sellPrice: sell.price,
          spreadPct: spread,
          estimatedGrossProfit: grossProfit,
        };

        opportunities.push(opportunity);

        logger.info(
          `🔍 Arbitrage detected: ${pairId} | ` +
            `Buy @ ${buy.price.toFixed(6)} (${buy.pool.dexName}) → ` +
            `Sell @ ${sell.price.toFixed(6)} (${sell.pool.dexName}) | ` +
            `Spread: ${(spread * 100).toFixed(3)}% | ` +
            `Est. profit: $${grossProfit.toFixed(2)}`
        );
      }
    }
  }

  // Sort by spread descending (best opportunities first)
  opportunities.sort((a, b) => b.spreadPct - a.spreadPct);

  logger.info(
    `Arbitrage scan complete: ${opportunities.length} opportunities found across ${priceMap.size} pairs`
  );

  return opportunities;
}
