import { flameWager } from "@/services/sdk"
import { USER_ACTIONS_QUERY } from "./graphql/queries"

/**
 * Fetch transaction history for a specific user address
 */
export const fetchUserActions = async (userAddress, vaultAddress = "%", limit = 20) => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(USER_ACTIONS_QUERY, { 
            user: userAddress, 
            vault: vaultAddress,
            limit 
        }).toPromise()
        
        if (result.error) {
            throw result.error
        }

        return result.data.userActions.map(action => ({
            id: action.id,
            vaultId: action.vaultId,
            type: action.actionType,
            assets: action.assets,
            shares: action.shares,
            timestamp: action.timestamp,
            hash: action.transactionHash
        }))
    } catch (error) {
        console.error(`Failed to fetch user actions for ${userAddress}:`, error)
        return []
    }
}
