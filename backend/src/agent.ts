/**
 * Agent Orchestration Module
 *
 * Main arbitrage loop that coordinates all modules:
 * Pool Discovery → Price Extraction → Arbitrage Detection →
 * Profitability Check → Transaction Building → Report
 */

import { ethers } from "ethers";
import { logger } from "./logger.js";
import type { AppConfig } from "./config.js";
import type { AgentReport, ProfitEvaluation, TradePayload } from "./types.js";
import { discoverPools, setNetworkId } from "./poolDiscovery.js";
import { extractPrices } from "./priceExtractor.js";
import { detectArbitrage } from "./arbitrageDetector.js";
import { evaluateProfitability } from "./profitCalculator.js";
import { buildTransactions } from "./transactionBuilder.js";

/**
 * Execute a single arbitrage scan cycle.
 *
 * @param config - Application configuration
 * @returns AgentReport with all findings
 */
export async function runArbitrageCycle(
  config: AppConfig
): Promise<AgentReport> {
  const startTime = Date.now();
  logger.info("═══════════════════════════════════════════════");
  logger.info("🚀 Starting arbitrage scan cycle");
  logger.info("═══════════════════════════════════════════════");

  const provider = new ethers.JsonRpcProvider(config.rpcUrl);

  // --- Step 1: Pool Discovery ---
  logger.info("📡 Step 1: Discovering pools...");
  setNetworkId(config.geckoNetworkId);
  const pools = await discoverPools(config.geckoNetworkId);

  if (pools.length === 0) {
    logger.warn("No pools found — skipping cycle");
    return createEmptyReport();
  }

  // --- Step 2: Price Extraction ---
  logger.info("📊 Step 2: Extracting prices...");
  const priceMap = extractPrices(pools);

  // --- Step 3: Arbitrage Detection ---
  logger.info("🔍 Step 3: Detecting arbitrage opportunities...");
  const opportunities = detectArbitrage(priceMap, 0);

  // --- Step 4: Profitability Evaluation ---
  logger.info("💰 Step 4: Evaluating profitability...");
  let evaluations: ProfitEvaluation[] = [];
  if (opportunities.length > 0) {
    evaluations = await evaluateProfitability(
      opportunities,
      provider,
      config.minProfitMargin,
      config.maxSlippage
    );
  } else {
    logger.info("No arbitrage opportunities found in this cycle");
  }

  // --- Step 5: Transaction Building ---
  logger.info("📝 Step 5: Building transactions...");
  let trades: TradePayload[] = [];
  const executable = evaluations.filter((e) => e.decision === "EXECUTE");
  if (executable.length > 0) {
    // In full production mode, user address would be provided
    trades = buildTransactions(
      evaluations,
      "0x0000000000000000000000000000000000000000", // placeholder — provided by OpenClaw/MCP
      config.chainId,
      config.maxSlippage
    );
  }

  // --- Report ---
  const report = createReport(pools.length, priceMap.size, evaluations, trades);
  printReport(report);

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  logger.info(`⏱️  Cycle completed in ${elapsed}s`);
  logger.info("═══════════════════════════════════════════════\n");

  return report;
}

function createEmptyReport(): AgentReport {
  return {
    timestamp: new Date().toISOString(),
    poolsDiscovered: 0,
    pairsAnalyzed: 0,
    opportunitiesFound: 0,
    evaluations: [],
    trades: [],
  };
}

function createReport(
  poolsDiscovered: number,
  pairsAnalyzed: number,
  evaluations: ProfitEvaluation[],
  trades: TradePayload[]
): AgentReport {
  return {
    timestamp: new Date().toISOString(),
    poolsDiscovered,
    pairsAnalyzed,
    opportunitiesFound: evaluations.length,
    evaluations,
    trades,
  };
}

function printReport(report: AgentReport): void {
  logger.info("\n📋 ═══ ARBITRAGE REPORT ═══");
  logger.info(`   Timestamp:        ${report.timestamp}`);
  logger.info(`   Pools discovered: ${report.poolsDiscovered}`);
  logger.info(`   Pairs analyzed:   ${report.pairsAnalyzed}`);
  logger.info(`   Opportunities:    ${report.opportunitiesFound}`);

  const execCount = report.evaluations.filter(
    (e) => e.decision === "EXECUTE"
  ).length;
  const skipCount = report.evaluations.filter(
    (e) => e.decision === "SKIP"
  ).length;
  logger.info(`   Decisions:        ${execCount} EXECUTE / ${skipCount} SKIP`);
  logger.info(`   Trades prepared:  ${report.trades.length}`);

  if (report.evaluations.length > 0) {
    logger.info("\n   Top opportunities:");
    for (const ev of report.evaluations.slice(0, 5)) {
      const opp = ev.opportunity;
      const emoji = ev.decision === "EXECUTE" ? "✅" : "⏭️";
      logger.info(
        `   ${emoji} ${opp.pairId}: ${(opp.spreadPct * 100).toFixed(3)}% spread | ` +
          `$${ev.netProfitUsd.toFixed(4)} net | ${ev.decision}`
      );
    }
  }

  logger.info("═══════════════════════════\n");
}
