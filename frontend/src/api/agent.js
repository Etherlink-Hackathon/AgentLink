/**
 * Agent API
 * Handles interaction with the Arbitrage Agent (Logger & Status)
 */

const LOGS_MOCK = [
    { id: 1, time: "10:42:01", msg: "Searching for arbitrage opportunities across Etherlink DEXs..." },
    { id: 2, time: "10:42:05", msg: "Scanning Curve (Etherlink) mBASIS / USDC pool liquidity: 2.95M" },
    { id: 3, time: "10:42:08", msg: "Scanning Oku Trade (Etherlink) USDC / WXTZ pool liquidity: 841.38K" },
    { id: 4, time: "10:42:12", msg: "Potential triangular arbitrage found: WXTZ -> USDC -> mTBILL -> WXTZ" },
    { id: 5, time: "10:42:15", msg: "Calculating optimal route and slippage (estimated profit: 0.42%)" },
    { id: 6, time: "10:42:18", msg: "Executing multi-hop arbitrage via ArbitrageVault..." },
    { id: 7, time: "10:42:22", msg: "Transaction confirmed. Hash: 0x742d...f44e" },
    { id: 8, time: "10:42:25", msg: "Arbitrage successful. Profit: +12.42 USDC" },
]

const TXS_MOCK = [
    { 
        time: "3/30/2026 - 14:52:23", 
        type: "Limit", 
        pair: "XTZ / WETH",
        dex: "Curve",
        direction: "Sell",
        size: "1,113.6155 XTZ", 
        profit: "+12.42 USDC",
        hash: "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" 
    },
    { 
        time: "3/30/2026 - 14:49:22", 
        type: "Limit", 
        pair: "WBTC / XTZ",
        dex: "Oku Trade",
        direction: "Buy",
        size: "0.00943755 WBTC", 
        profit: "+28.15 USDC",
        hash: "0x89221f1912252a3b844Bc454e4438f44e12345678" 
    },
    { 
        time: "3/30/2026 - 14:45:49", 
        type: "Limit", 
        pair: "stXTZ / WXTZ",
        dex: "Curve",
        direction: "Buy",
        size: "250.00 WXTZ", 
        profit: "-0.50 USDC",
        hash: "0xabcdef1234567890abcdef1234567890abcdef12" 
    },
]

/**
 * Fetch live logs from the agent
 */
export const fetchAgentLogs = async () => {
    return LOGS_MOCK
}

/**
 * Fetch agent transaction history
 */
export const fetchAgentTransactions = async () => {
    return TXS_MOCK
}

/**
 * Fetch agent execution status
 */
export const fetchAgentStatus = async () => {
    return {
        is_running: true,
        last_scan: new Date().toISOString(),
        total_profit_24h: "$142.20",
        active_strategies: 4
    }
}
