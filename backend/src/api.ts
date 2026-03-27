import express from "express";
import cors from "cors";
import { discoverPools } from "./poolDiscovery.js";
import { logger } from "./logger.js";

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// In-memory cache for discovered pools
let cachedPools: any[] = [];
let lastFetch = 0;
const CACHE_TTL = 30000; // 30 seconds

app.get("/api/pools", async (req, res) => {
	try {
		const now = Date.now();
		if (now - lastFetch > CACHE_TTL || cachedPools.length === 0) {
			logger.info("API: Fetching fresh pools from GeckoTerminal...");
			const pools = await discoverPools("etherlink", 1); // Just 1 page for speed
			cachedPools = pools.map(pool => ({
				dex: pool.dexName,
				vault: `${pool.token0.symbol}/${pool.token1.symbol}`,
				allocation: "25%", // Mock allocation logic for now
				liquidity: `$${(pool.tvlUsd / 1000000).toFixed(1)}M`
			}));
			lastFetch = now;
		}
		res.json(cachedPools);
	} catch (error) {
		logger.error("API error fetching pools", { error });
		res.status(500).json({ error: "Failed to fetch pools" });
	}
});

app.get("/api/stats", (req, res) => {
	// Mock stats for now, can be aggregated from pools later
	res.json({
		tvl: 1250000,
		apy: 12.5,
		revenue: 625,
		strategies: 4
	});
});

app.get("/api/logs", (req, res) => {
	// Return some mock logs for now, or read from agent.log if needed
	const timestamp = new Date().toLocaleTimeString();
	res.json([
		{ time: `[${timestamp}]`, msg: "Arbitrage opportunity detected. Executing swap..." },
		{ time: `[${timestamp}]`, msg: "Scanning DEX pools on Etherlink Mainnet..." },
		{ time: `[${timestamp}]`, msg: "Price discrepancy found: WETH/USDC (1.2%)" },
		{ time: `[${timestamp}]`, msg: "Transaction confirmed: 0x5e2...f3a" },
		{ time: `[${timestamp}]`, msg: "Yield harvested: $12.45" }
	]);
});

export function startServer() {
	app.listen(PORT, () => {
		logger.info(`🚀 API Server running at http://localhost:${PORT}`);
	});
}
