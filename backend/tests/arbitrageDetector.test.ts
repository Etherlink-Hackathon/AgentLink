import { describe, it, expect } from "vitest";
import { detectArbitrage } from "../src/arbitrageDetector.js";
import type { TokenPairPrice, Token, Pool } from "../src/types.js";

const mockToken: Token = {
  address: "0x1",
  symbol: "WETH",
  name: "Wrapped Ether",
  decimals: 18,
};

const mockQuote: Token = {
  address: "0x2",
  symbol: "USDC",
  name: "USD Coin",
  decimals: 6,
};

const basePoolParams = {
  token0: mockToken,
  token1: mockQuote,
  reserve0: 0n,
  reserve1: 0n,
  feeBps: 30,
  tvlUsd: 50000,
};

const pool1: Pool = {
  ...basePoolParams,
  address: "0xA",
  dexName: "DexA",
  price0: 2000,
  price1: 1 / 2000,
};

const pool2: Pool = {
  ...basePoolParams,
  address: "0xB",
  dexName: "DexB",
  price0: 2050, // More expensive correctly generates a spread
  price1: 1 / 2050,
};

const pool3: Pool = {
  ...basePoolParams,
  address: "0xC",
  dexName: "DexC",
  price0: 2005, // Too small spread if minSpread is high
  price1: 1 / 2005,
};

describe("arbitrageDetector", () => {
  it("should detect spread between pools", () => {
    const priceMap = new Map<string, TokenPairPrice[]>([
      [
        "USDC/WETH",
        [
          { baseToken: mockToken, quoteToken: mockQuote, pool: pool1, price: pool1.price0 },
          { baseToken: mockToken, quoteToken: mockQuote, pool: pool2, price: pool2.price0 },
        ],
      ],
    ]);

    const result = detectArbitrage(priceMap, 0);

    expect(result).toHaveLength(1);
    expect(result[0].buyPool.dexName).toBe("DexA");
    expect(result[0].sellPool.dexName).toBe("DexB");
    expect(result[0].spreadPct).toBeCloseTo(0.025, 4); // (2050 - 2000) / 2000
    expect(result[0].estimatedGrossProfit).toBeGreaterThan(0);
  });

  it("should ignore spreads below minSpreadPct", () => {
    const priceMap = new Map<string, TokenPairPrice[]>([
      [
        "USDC/WETH",
        [
          { baseToken: mockToken, quoteToken: mockQuote, pool: pool1, price: pool1.price0 },
          { baseToken: mockToken, quoteToken: mockQuote, pool: pool3, price: pool3.price0 }, // 2005 vs 2000 = 0.25% spread
        ],
      ],
    ]);

    // Require 1% spread, should yield 0 results
    const result = detectArbitrage(priceMap, 0.01);
    expect(result).toHaveLength(0);
    
    // Require 0% spread, should yield 1 result
    const result2 = detectArbitrage(priceMap, 0);
    expect(result2).toHaveLength(1);
  });
});
