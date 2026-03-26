/**
 * Profitability Calculator Module
 *
 * Evaluates whether an arbitrage opportunity is worth executing
 * after accounting for gas costs, fees, and slippage.
 */

import { ethers } from "ethers";
import { logger } from "./logger.js";
import type { ArbitrageOpportunity, ProfitEvaluation } from "./types.js";

/** Current approximate XTZ price in USD (should be fetched dynamically in production) */
const XTZ_PRICE_USD = 1.5;

/** Average gas per swap on Etherlink (estimated) */
const GAS_PER_SWAP = 150_000n;

/** Number of swaps in a simple arbitrage (buy + sell) */
const SWAPS_PER_ARB = 2;

/**
 * Evaluate profitability of arbitrage opportunities.
 *
 * @param opportunities - Detected arbitrage opportunities
 * @param provider - Ethers provider for gas price estimation
 * @param minProfitMargin - Minimum net margin to execute (e.g. 0.005 = 0.5%)
 * @param maxSlippage - Maximum slippage tolerance
 * @returns Array of evaluated opportunities with EXECUTE/SKIP decisions
 */
export async function evaluateProfitability(
  opportunities: ArbitrageOpportunity[],
  provider: ethers.JsonRpcProvider,
  minProfitMargin: number = 0.005,
  maxSlippage: number = 0.01
): Promise<ProfitEvaluation[]> {
  const evaluations: ProfitEvaluation[] = [];

  // Fetch current gas price once
  let gasPriceWei: bigint;
  try {
    const feeData = await provider.getFeeData();
    gasPriceWei = feeData.gasPrice ?? ethers.parseUnits("1", "gwei");
  } catch (error) {
    logger.warn("Failed to fetch gas price, using default 1 gwei", { error });
    gasPriceWei = ethers.parseUnits("1", "gwei");
  }

  for (const opp of opportunities) {
    const evaluation = evaluateSingle(
      opp,
      gasPriceWei,
      minProfitMargin,
      maxSlippage
    );
    evaluations.push(evaluation);
  }

  const execCount = evaluations.filter((e) => e.decision === "EXECUTE").length;
  const skipCount = evaluations.filter((e) => e.decision === "SKIP").length;

  logger.info(
    `Profitability evaluation: ${execCount} EXECUTE, ${skipCount} SKIP out of ${evaluations.length} opportunities`
  );

  return evaluations;
}

/**
 * Evaluate a single arbitrage opportunity.
 */
function evaluateSingle(
  opp: ArbitrageOpportunity,
  gasPriceWei: bigint,
  minProfitMargin: number,
  maxSlippage: number
): ProfitEvaluation {
  // Calculate total gas cost
  const totalGasUnits = GAS_PER_SWAP * BigInt(SWAPS_PER_ARB);
  const gasCostWei = gasPriceWei * totalGasUnits;
  const gasCostXtz = parseFloat(ethers.formatEther(gasCostWei));
  const gasCostUsd = gasCostXtz * XTZ_PRICE_USD;

  // Account for slippage — reduce expected profit
  const slippageAdjustedProfit =
    opp.estimatedGrossProfit * (1 - maxSlippage);

  // Account for DEX fees (already baked into pool prices from GeckoTerminal,
  // but add a safety buffer)
  const feeBuffer = opp.estimatedGrossProfit * 0.003; // 0.3% additional buffer

  // Net profit
  const netProfitUsd = slippageAdjustedProfit - gasCostUsd - feeBuffer;

  // Minimum absolute profit threshold
  const minAbsoluteProfit = gasCostUsd * (1 + minProfitMargin / 0.005);

  // Decision logic
  let decision: "EXECUTE" | "SKIP";
  let reason: string;

  if (netProfitUsd <= 0) {
    decision = "SKIP";
    reason = `Net profit ($${netProfitUsd.toFixed(4)}) is negative after gas ($${gasCostUsd.toFixed(4)}) and slippage`;
  } else if (opp.spreadPct < minProfitMargin) {
    decision = "SKIP";
    reason = `Spread (${(opp.spreadPct * 100).toFixed(3)}%) below min margin (${(minProfitMargin * 100).toFixed(1)}%)`;
  } else if (netProfitUsd < minAbsoluteProfit) {
    decision = "SKIP";
    reason = `Net profit ($${netProfitUsd.toFixed(4)}) below minimum threshold ($${minAbsoluteProfit.toFixed(4)})`;
  } else if (
    opp.buyPool.tvlUsd < 1000 ||
    opp.sellPool.tvlUsd < 1000
  ) {
    decision = "SKIP";
    reason = `Insufficient liquidity: buy pool TVL $${opp.buyPool.tvlUsd.toFixed(0)}, sell pool TVL $${opp.sellPool.tvlUsd.toFixed(0)}`;
  } else {
    decision = "EXECUTE";
    reason = `Profitable: $${netProfitUsd.toFixed(4)} net after ${(opp.spreadPct * 100).toFixed(3)}% spread`;
  }

  const evaluation: ProfitEvaluation = {
    opportunity: opp,
    gasCostXtz,
    gasCostUsd,
    netProfitUsd,
    decision,
    reason,
  };

  const emoji = decision === "EXECUTE" ? "✅" : "⏭️";
  logger.info(
    `${emoji} ${opp.pairId}: ${decision} — ${reason}`
  );

  return evaluation;
}
