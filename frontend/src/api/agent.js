/**
 * Agent API
 * Handles interaction with the Arbitrage Agent (Logger & Status)
 */

const LOGS_MOCK = [
    { id: 1, timestamp: new Date().toISOString(), level: "info", message: "Searching for arbitrage opportunities..." },
    { id: 2, timestamp: new Date().toISOString(), level: "success", message: "Found opportunity: WETH/USDT on Uniswap V3 (0.8% profit)" },
    { id: 3, timestamp: new Date().toISOString(), level: "info", message: "Executing cross-DEX swap..." },
    { id: 4, timestamp: new Date().toISOString(), level: "info", message: "Transaction confirmed on Etherlink." },
]

/**
 * Fetch live logs from the agent
 */
export const fetchAgentLogs = async () => {
    // In a real scenario, this would call the backend API or a WebSocket
    return LOGS_MOCK
}

/**
 * Fetch agent execution status
 */
export const fetchAgentStatus = async () => {
    return {
        is_running: true,
        last_scan: new Date().toISOString(),
        total_profit_24h: "$1,240.20",
        active_strategies: 4
    }
}
