/**
 * Transaction Builder Module
 *
 * Builds unsigned swap transaction payloads targeting the ArbitrageVault.
 * The Strategist (Agent) will submit this payload.
 */

import { ethers } from "ethers";
import { logger } from "./logger.js";
import type { ProfitEvaluation, TradePayload } from "./types.js";

/** ArbitrageVault minimal ABI for executeArbitrage */
const VAULT_ABI = [
  "function executeArbitrage(address dexBuy, address dexSell, address tokenTrade, uint256 amountBase) external"
];

// Address of the deployed ArbitrageVault (placeholder for now)
const VAULT_ADDRESS = "0x0000000000000000000000000000000000000000";

/**
 * Build unsigned transaction payloads mapping to the ArbitrageVault.
 *
 * @param evaluations - Profit evaluations with EXECUTE decisions
 * @param userAddress - The agent's address (Strategist wallet)
 * @param chainId - Target chain ID
 * @param maxSlippage - Maximum slippage tolerance (handled mathematically inside Vault, but logic remains for compat)
 * @returns Array of unsigned TradePayload objects
 */
export function buildTransactions(
  evaluations: ProfitEvaluation[],
  userAddress: string,
  chainId: number,
  maxSlippage: number = 0.01
): TradePayload[] {
  const trades: TradePayload[] = [];

  const executableTrades = evaluations.filter(
    (e) => e.decision === "EXECUTE"
  );

  if (executableTrades.length === 0) {
    logger.info("No executable trades to build transactions for");
    return trades;
  }

  const iface = new ethers.Interface(VAULT_ABI);

  for (const evaluation of executableTrades) {
    try {
      const opp = evaluation.opportunity;

      // Estimate amountBase as 1% of the smallest pool TVL
      const amountBase = estimateTradeAmount(
        Math.min(opp.buyPool.tvlUsd, opp.sellPool.tvlUsd),
        opp.quoteToken.decimals
      );

      // payload for executeArbitrage
      const data = iface.encodeFunctionData("executeArbitrage", [
        opp.buyPool.address, // Buy Dex Router
        opp.sellPool.address, // Sell Dex Router
        opp.baseToken.address, // The token being traded for arbitrage
        amountBase
      ]);

      const tx: TradePayload = {
        to: VAULT_ADDRESS,
        data,
        value: "0",
        chainId,
        gasLimit: "500000",
        description: `Strategist exec: Arb ${opp.baseToken.symbol} from ${opp.buyPool.dexName} to ${opp.sellPool.dexName} | Est. net profit: $${evaluation.netProfitUsd.toFixed(4)}`,
      };

      trades.push(tx);

      logger.info(
        `📝 Built strategist payload for ${opp.pairId}: ` +
          `Vault.executeArbitrage(${opp.buyPool.address}, ${opp.sellPool.address}, ${opp.baseToken.address}, ${amountBase})`
      );
    } catch (error) {
      logger.error(`Failed to build strategist transaction for ${evaluation.opportunity.pairId}`, {
        error,
      });
    }
  }

  logger.info(`Built ${trades.length} vault payloads for ${executableTrades.length} opportunities`);
  return trades;
}

/**
 * Estimate trade amount as 1% of pool TVL,
 * converted to token's smallest unit.
 */
function estimateTradeAmount(poolTvlUsd: number, tokenDecimals: number): bigint {
  const tradeUsd = poolTvlUsd * 0.01; // 1% of TVL
  return ethers.parseUnits(tradeUsd.toFixed(6), tokenDecimals);
}
