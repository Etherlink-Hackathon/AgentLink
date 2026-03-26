import { describe, it, expect } from "vitest";
import { ethers } from "ethers";
import { evaluateProfitability } from "../src/profitCalculator.js";
import type { ArbitrageOpportunity, Pool, Token } from "../src/types.js";

const mockToken: Token = {
  address: "0x123",
  symbol: "WXTZ",
  name: "Wrapped XTZ",
  decimals: 18,
};

const mockQuote: Token = {
  address: "0x456",
  symbol: "USDC",
  name: "USD Coin",
  decimals: 6,
};

const mockPoolA: Pool = {
  address: "0xAAA",
  dexName: "DexA",
  token0: mockToken,
  token1: mockQuote,
  reserve0: 1000n,
  reserve1: 1500n,
  feeBps: 30,
  price0: 1.5,
  price1: 0.666,
  tvlUsd: 100000, // Sufficient liquidity
};

const mockPoolB: Pool = {
  address: "0xBBB",
  dexName: "DexB",
  token0: mockToken,
  token1: mockQuote,
  reserve0: 1000n,
  reserve1: 1600n,
  feeBps: 30,
  price0: 1.6,
  price1: 0.625,
  tvlUsd: 100000,
};

// Mock provider returning fixed gas price
const mockProvider = {
  getFeeData: async () => ({
    gasPrice: ethers.parseUnits("1", "gwei"),
  }),
} as unknown as ethers.JsonRpcProvider;

describe("profitCalculator", () => {
  it("should EXECUTE highly profitable opportunity", async () => {
    const opp: ArbitrageOpportunity = {
      pairId: "USDC/WXTZ",
      baseToken: mockToken,
      quoteToken: mockQuote,
      buyPool: mockPoolA,
      sellPool: mockPoolB,
      buyPrice: 1.5,
      sellPrice: 1.6,
      spreadPct: 0.066, // 6.6% spread (well above gas/margin)
      estimatedGrossProfit: 50, // $50 gross profit
    };

    const result = await evaluateProfitability(
      [opp],
      mockProvider,
      0.005, // 0.5% min margin
      0.01 // 1% max slippage
    );

    expect(result).toHaveLength(1);
    expect(result[0].decision).toBe("EXECUTE");
    expect(result[0].netProfitUsd).toBeGreaterThan(0);
  });

  it("should SKIP due to negative net profit (gas > profit)", async () => {
    const opp: ArbitrageOpportunity = {
      pairId: "USDC/WXTZ",
      baseToken: mockToken,
      quoteToken: mockQuote,
      buyPool: mockPoolA,
      sellPool: mockPoolB,
      buyPrice: 1.5,
      sellPrice: 1.51,
      spreadPct: 0.006, // 0.6% spread
      estimatedGrossProfit: 0.0001, // $0.0001 gross profit (won't cover gas)
    };

    const result = await evaluateProfitability([opp], mockProvider);

    expect(result).toHaveLength(1);
    expect(result[0].decision).toBe("SKIP");
    expect(result[0].reason).toMatch(/is negative/);
  });

  it("should SKIP due to insufficient liquidity", async () => {
    const lowLiquidityPool = { ...mockPoolA, tvlUsd: 500 }; // < 1000
    
    const opp: ArbitrageOpportunity = {
      pairId: "USDC/WXTZ",
      baseToken: mockToken,
      quoteToken: mockQuote,
      buyPool: lowLiquidityPool,
      sellPool: mockPoolB,
      buyPrice: 1.5,
      sellPrice: 1.6,
      spreadPct: 0.066,
      estimatedGrossProfit: 50,
    };

    const result = await evaluateProfitability([opp], mockProvider);

    expect(result).toHaveLength(1);
    expect(result[0].decision).toBe("SKIP");
    expect(result[0].reason).toMatch(/Insufficient liquidity/);
  });
});
