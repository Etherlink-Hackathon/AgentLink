import axios from "axios"
import mockVaults from "./vaults.json"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:3000"

/**
 * Fetch all active vaults (mapped from DEX pools)
 */
export const fetchVaults = async () => {
    try {
        const response = await axios.get(`${API_BASE}/api/pools`)
        const pools = response.data
        
        // Map backend pools to vault structure
        return pools.map(pool => ({
            id: pool.address,
            name: pool.name || `${pool.token0.symbol}/${pool.token1.symbol} Arbitrage`,
            strategyType: "Cross-DEX Arbitrage",
            status: pool.status || "active",
            tvl: pool.tvl || Math.floor(Math.random() * 1000000) + 100000,
            apy: pool.apy || (Math.random() * 15 + 5).toFixed(1),
            revenue: pool.revenue || 0,
            strategies: pool.strategies || 1,
            tags: ["High Yield", pool.dex, "Etherlink"],
            poolData: pool
        }))
    } catch (error) {
        console.warn("Backend unavailable, using mock vaults.")
        return mockVaults.map(pool => ({
            id: pool.address,
            name: pool.name || `${pool.token0.symbol}/${pool.token1.symbol} Arbitrage`,
            strategyType: "Cross-DEX Arbitrage",
            status: pool.status,
            tvl: pool.tvl,
            apy: pool.apy,
            revenue: pool.revenue,
            strategies: pool.strategies,
            tags: ["High Yield", pool.dex, "Etherlink"],
            poolData: pool
        }))
    }
}

/**
 * Fetch a single vault by ID
 */
export const fetchVaultById = async (id) => {
    try {
        const response = await axios.get(`${API_BASE}/api/pools`)
        const pool = response.data.find(p => p.address === id)
        
        if (!pool) throw new Error("Vault not found")

        return {
            id: pool.address,
            name: `${pool.token0.symbol}/${pool.token1.symbol} Arbitrage`,
            strategyType: "Cross-DEX Arbitrage",
            status: "active",
            tvl: pool.tvl || Math.floor(Math.random() * 1000000) + 100000,
            apy: pool.apy || (Math.random() * 15 + 5).toFixed(1),
            tags: ["High Yield", pool.dex, "Etherlink"],
            description: `This strategy exploits price discrepancies for the ${pool.token0.symbol}/${pool.token1.symbol} pair on ${pool.dex}.`,
            poolData: pool
        }
    } catch (error) {
        const pool = mockVaults.find(p => p.address === id)
        if (!pool) return null

        return {
            id: pool.address,
            name: `${pool.token0.symbol}/${pool.token1.symbol} Arbitrage`,
            strategyType: "Cross-DEX Arbitrage",
            status: pool.status,
            tvl: pool.tvl,
            apy: pool.apy,
            tags: ["High Yield", pool.dex, "Etherlink"],
            description: `[MOCK] This strategy exploits price discrepancies for the ${pool.token0.symbol}/${pool.token1.symbol} pair on ${pool.dex}.`,
            poolData: pool
        }
    }
}
