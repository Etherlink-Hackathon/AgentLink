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

        return result.data.dex_pools.map(pool => ({
            id: pool.id,
            address: pool.address,
            name: pool.name,
            tvl_usd: pool.tvl_usd,
            tvl_xtz: pool.tvl_xtz,
            last_updated: pool.last_updated,
            token_a: pool.token_a,
            token_b: pool.token_b
        }))
    } catch (error) {
        console.error("Failed to fetch DEX pools via GraphQL:", error)
        return []
    }
}
