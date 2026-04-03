import { flameWager } from "@/services/sdk"
import { VAULTS_QUERY, VAULT_BY_ADDRESS_QUERY } from "./graphql/queries"

/**
 * Fetch all active vaults with their snapshots
 */
export const fetchVaults = async () => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(VAULTS_QUERY).toPromise()

        if (result.error) {
            throw result.error
        }

        return result.data.vaults.map(vault => {
            const latestSnapshot = vault.snapshots[0] || {}

            return {
                id: vault.address,
                address: vault.address,
                creator: vault.creator,
                name: vault.name,
                symbol: vault.symbol,
                strategyType: "Cross-DEX Arbitrage",
                status: "active",
                tvl: latestSnapshot.totalAssets || 0,
                apy: latestSnapshot.apy || 0,
                revenue: latestSnapshot.yield1d || 0,
                created_at: vault.createdAt,
                tags: ["High Yield", "Etherlink", "Arbitrage"],
                asset_address: vault.assetAddress,
                vaultsPools: vault.vaultsPools
            }
        })
    } catch (error) {
        console.error("Failed to fetch vaults via GraphQL:", error)
        return []
    }
}

/**
 * Fetch a single vault by its address
 */
export const fetchVaultById = async (address) => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(VAULT_BY_ADDRESS_QUERY, { address }).toPromise()

        if (result.error) {
            throw result.error
        }

        const vault = result.data.vault
        if (!vault) throw new Error("Vault not found")

        const latestSnapshot = vault.snapshots[0] || {}

        return {
            id: vault.address,
            address: vault.address,
            name: vault.name,
            symbol: vault.symbol,
            strategyType: "Cross-DEX Arbitrage",
            status: "active",
            tvl: latestSnapshot.totalAssets || 0,
            apy: latestSnapshot.apy || 0,
            tags: ["High Yield", "Etherlink", "Arbitrage"],
            description: `This strategy exploits price discrepancies for the Etherlink Dex Pools.`,
            yield_history: vault.yields || [],
            created_at: vault.createdAt,
            asset_address: vault.assetAddress,
            vaultsPools: vault.vaultsPools
        }
    } catch (error) {
        console.error(`Failed to fetch vault ${address} via GraphQL:`, error)
        return null
    }
}
