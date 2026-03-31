import { flameWager } from "@/services/sdk"
import { AGENT_DECISIONS_QUERY, AGENT_EXECUTIONS_QUERY } from "./graphql/queries"
import { DateTime } from "luxon"

/**
 * Fetch live logs from the agent (mapped from decisions)
 */
export const fetchAgentLogs = async (limit = 20) => {
    try {
        if (!flameWager.gql) return []

        const result = await flameWager.gql.query(AGENT_DECISIONS_QUERY, { limit }).toPromise()
        
        if (result.error) {
            throw result.error
        }

        return result.data.agentDecisions.map(log => ({
            id: log.id,
            vaultId: log.vaultId,
            status: log.status,
            heuristicsVerdict: log.heuristicsVerdict,
            geminiVerdict: log.geminiVerdict,
            opportunityDetails: typeof log.opportunityDetails === 'string' 
                ? JSON.parse(log.opportunityDetails) 
                : log.opportunityDetails,
            txHash: log.txHash,
            error: log.error,
            createdAt: log.createdAt
        }))
    } catch (error) {
        console.error("Failed to fetch agent logs via GraphQL:", error)
        return []
    }
}

/**
 * Fetch recent successful arbitrage executions
 */
export const fetchAgentTransactions = async (limit = 20) => {
    try {
        if (!flameWager.gql) {
            throw new Error("GraphQL client not initialized")
        }

        const result = await flameWager.gql.query(AGENT_EXECUTIONS_QUERY, { limit }).toPromise()
        
        if (result.error) {
            throw result.error
        }

        return result.data.agentExecutions.map(tx => ({
            id: tx.id,
            vaultId: tx.vaultId,
            strategist: tx.strategist,
            hops: tx.hops,
            routeDetails: typeof tx.routeDetails === 'string'
                ? JSON.parse(tx.routeDetails)
                : tx.routeDetails,
            profit: tx.profit,
            timestamp: tx.timestamp,
            hash: tx.transactionHash
        }))
    } catch (error) {
        console.error("Failed to fetch agent transactions via GraphQL:", error)
        return []
    }
}

/**
 * Fetch agent execution status
 */
export const fetchAgentStatus = async () => {
    try {
        const logs = await fetchAgentLogs()
        const txs = await fetchAgentTransactions()
        
        const lastLog = logs[0]
        const totalProfit = txs.reduce((acc, tx) => acc + parseFloat(tx.profit || 0), 0)

        return {
            is_running: true,
            last_scan: lastLog ? lastLog.time : new Date().toISOString(),
            total_profit_24h: `$${totalProfit.toFixed(2)}`,
            active_strategies: 4
        }
    } catch (error) {
        return {
            is_running: false,
            last_scan: "N/A",
            total_profit_24h: "$0.00",
            active_strategies: 0
        }
    }
}
