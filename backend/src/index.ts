/**
 * Etherlink Omni-DEX Arbitrage Agent — Entry Point
 *
 * Initializes configuration, sets up logging,
 * and starts the arbitrage scan loop.
 */

import { loadConfig } from "./config.js";
import { createLogger, setLogger, logger } from "./logger.js";
import { runArbitrageCycle } from "./agent.js";
import { startServer } from "./api.js";

async function main(): Promise<void> {
  const config = loadConfig();

  // Initialize logger with configured level
  const appLogger = createLogger(config.logLevel);
  setLogger(appLogger);

  startServer();

  logger.info("╔══════════════════════════════════════════════╗");
  logger.info("║  Etherlink Omni-DEX Arbitrage Agent          ║");
  logger.info("║  Powered by OpenClaw + etherlink-mcp-server  ║");
  logger.info("╚══════════════════════════════════════════════╝");
  logger.info("");
  logger.info(`  Network:        Etherlink Mainnet (Chain ${config.chainId})`);
  logger.info(`  RPC:            ${config.rpcUrl}`);
  logger.info(`  Min margin:     ${(config.minProfitMargin * 100).toFixed(1)}%`);
  logger.info(`  Max slippage:   ${(config.maxSlippage * 100).toFixed(1)}%`);
  logger.info(`  Loop interval:  ${config.loopIntervalMs / 1000}s`);
  logger.info("");

  // Run initial cycle immediately
  logger.info("Running initial arbitrage scan...");
  await runArbitrageCycle(config);

  // Start periodic loop
  logger.info(
    `Scheduling next scan in ${config.loopIntervalMs / 1000}s (${config.loopIntervalMs / 60000} min)`
  );

  setInterval(async () => {
    try {
      await runArbitrageCycle(config);
    } catch (error) {
      logger.error("Arbitrage cycle failed", { error });
    }
  }, config.loopIntervalMs);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
