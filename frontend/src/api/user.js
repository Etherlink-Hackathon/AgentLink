import { flameWager } from "@/services/sdk"
import { USER_ACTIONS_QUERY, USER_STATISTICS_QUERY } from "./graphql/queries"

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

/**
 * Fetch user portfolio statistics from the indexed materialized view.
 * Additionally enriches with live on-chain data: shares balance and redeemable assets.
 * 
 * @param {string} userAddress - The user wallet address (lowercase)
 * @param {string} [vaultAddress] - Optional vault address to query on-chain shares for
 * @returns {object} stats including netPosition, totalShares, redeemableAssets, totalRewardsEarned
 */
export const fetchUserStatistics = async (userAddress, vaultAddress = null) => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(USER_STATISTICS_QUERY, {
            address: userAddress.toLowerCase(),
            vault: vaultAddress || "%"
        }).toPromise()

        if (result.error) {
            throw result.error
        }

        const stats = result.data?.userStatistics?.[0] || null

        // Enrich with live on-chain data if vault is specified and SDK is connected
        let onChainShares = "0"
        let redeemableAssets = "0"

        if (vaultAddress && flameWager.signer) {
            try {
                const vault = flameWager.vaults[vaultAddress.toLowerCase()]
                if (vault) {
                    const shares = await vault.balanceOf(userAddress)
                    onChainShares = shares.toString()
                    if (shares > 0n) {
                        const assets = await vault.previewRedeem(shares)
                        redeemableAssets = assets.toString()
                    }
                }
            } catch (chainErr) {
                console.warn("Failed to fetch on-chain vault data:", chainErr)
            }
        }

        return {
            // From indexer (historical aggregate)
            netPosition: stats?.netPosition || "0",
            totalDeposited: stats?.totalDeposited || "0",
            totalWithdrawn: stats?.totalWithdrawn || "0",
            totalShares: stats?.totalShares || "0",
            totalRewardsEarned: stats?.totalRewardsEarned || "0",
            vaultsParticipated: stats?.vaultsParticipated || 0,
            totalActions: stats?.totalActions || 0,
            depositCount: stats?.depositCount || 0,
            withdrawalCount: stats?.withdrawalCount || 0,
            firstActionAt: stats?.firstActionAt || null,
            lastActionAt: stats?.lastActionAt || null,
            // From on-chain (live)
            onChainShares,
            redeemableAssets,
        }
    } catch (error) {
        console.error(`Failed to fetch user statistics for ${userAddress}:`, error)
        return {
            netPosition: "0",
            totalDeposited: "0",
            totalWithdrawn: "0",
            totalShares: "0",
            totalRewardsEarned: "0",
            vaultsParticipated: 0,
            totalActions: 0,
            depositCount: 0,
            withdrawalCount: 0,
            firstActionAt: null,
            lastActionAt: null,
            onChainShares: "0",
            redeemableAssets: "0",
        }
    }
}
