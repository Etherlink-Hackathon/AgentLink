import axios from "axios"
import mockVaults from "./vaults.json"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:3000"

/**
 * Fetch all active vaults (mapped from DEX pools)
 */
export const fetchVaults = async () => {
    try {
        const response = await axios.get(`${API_BASE}/api/vaults`)
        const vaults = response.data
        
        // Map backend pools to vault structure
        return vaults.map(vault => ({
            id: vault.address,
            address: vault.address,
            name: vault.name,
            strategyType: "Cross-DEX Arbitrage",
            status: vault.status || "active",
            tvl: vault.tvl || Math.floor(Math.random() * 1000000) + 100000,
            apy: vault.apy || (Math.random() * 15 + 5).toFixed(1),
            revenue: vault.revenue || 0,
            strategies: vault.strategies || 1,
            tags: ["High Yield", vault.dex, "Etherlink"],
            poolData: vault
        }))
    } catch (error) {
        console.warn("Backend unavailable, using mock vaults.")
        return mockVaults.map(vault => ({
            id: vault.address,
            address: vault.address || process.env.VITE_VAULT_ADDRESS,
            name: vault.name,
            strategyType: "Cross-DEX Arbitrage",
            status: vault.status,
            tvl: vault.tvl,
            apy: vault.apy,
            revenue: vault.revenue,
            strategies: vault.strategies,
            tags: ["High Yield", vault.dex, "Etherlink"],
            poolData: vault
        }))
    }
}

/**
 * Fetch a single vault by ID
 */
export const fetchVaultById = async (id) => {
    try {
        const response = await axios.get(`${API_BASE}/api/vaults`)
        const vault = response.data.find(v => v.address === id)
        
        if (!vault) throw new Error("Vault not found")

        return {
            id: vault.address,
            address: vault.address,
            name: vault.name,
            strategyType: "Cross-DEX Arbitrage",
            status: "active",
            tvl: vault.tvl || Math.floor(Math.random() * 1000000) + 100000,
            apy: vault.apy || (Math.random() * 15 + 5).toFixed(1),
            tags: ["High Yield", vault.dex, "Etherlink"],
            description: `This strategy exploits price discrepancies for the Etherlink Dex Pools.`,
            poolData: vault
        }
    } catch (error) {
        const vault = mockVaults.find(v => v.address === id)
        if (!vault) return null

        return {
            id: vault.address,
            address: vault.address,
            name: vault.name,
            strategyType: "Cross-DEX Arbitrage",
            status: vault.status,
            tvl: vault.tvl,
            apy: vault.apy,
            tags: ["High Yield", vault.dex, "Etherlink"],
            description: `[MOCK] This strategy exploits price discrepancies for the Etherlink Dex Pools.`,
            poolData: vault
        }
    }
}
