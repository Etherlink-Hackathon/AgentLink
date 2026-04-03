import { flameWager } from "@/services/sdk"
import { DEX_POOLS_QUERY } from "./graphql/queries"

/**
 * Fetch all whitelisted DEX pools from the indexer
 */
export const fetchPools = async () => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(DEX_POOLS_QUERY).toPromise()
        if (result.error) {
            throw result.error
        }

        return result.data.dexPools.map(pool => ({
            id: pool.id,
            address: pool.address,
            name: pool.name,
            tvl_usd: pool.tvlUsd,
            tvl_xtz: pool.tvlXtz,
            last_updated: pool.lastUpdated,
            token_a: pool.tokenA,
            token_b: pool.tokenB
        }))
    } catch (error) {
        console.error("Failed to fetch DEX pools via GraphQL:", error)
        return []
    }
}
