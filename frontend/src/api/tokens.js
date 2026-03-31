import { flameWager } from "@/services/sdk"
import { TOKENS_QUERY } from "./graphql/queries"

/**
 * Fetch all available tokens from the indexer
 */
export const fetchTokens = async () => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(TOKENS_QUERY).toPromise()
        
        if (result.error) {
            throw result.error
        }

        return result.data.tokens.map(token => ({
            id: token.id,
            address: token.address,
            name: token.name,
            symbol: token.symbol,
            decimals: token.decimals
        }))
    } catch (error) {
        console.error("Failed to fetch tokens via GraphQL:", error)
        return []
    }
}
