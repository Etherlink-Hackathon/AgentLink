/**
 * Fetch all tokens
 */
export const TOKENS_QUERY = `
  query GetTokens {
    tokens: tokens(order_by: { symbol: asc }) {
      id
      address
      name
      symbol
      decimals
    }
  }
`

/**
 * Fetch all vaults with latest snapshots
 */
export const VAULTS_QUERY = `
  query GetVaults {
  vaults: vaults(order_by: {name: asc}) {
    address
    name
    symbol
    assetAddress
    createdAt
    snapshots: snapshots(order_by: {timestamp: desc}, limit: 1) {
      totalAssets
      totalSupply
      yield1d
      yield1w
      yield1m
      apy
      timestamp
      vaultId
    }
    strategist
    creator
    vaultsPools {
      dexPools {
        address
        name
        tokenA {
          address
          decimals
          name
          symbol
        }
        tokenB {
          address
          decimals
          name
          symbol
        }
      }
    }
  }
}

`

/**
 * Fetch a single vault by its address
 */
export const VAULT_BY_ADDRESS_QUERY = `
  query GetVault($address: String!) {
    vault: vaultsByPk(address: $address) {
      address
      creator
      name
      symbol
      assetAddress
      createdAt
      snapshots: snapshots(order_by: { timestamp: desc }, limit: 1) {
        totalAssets
        totalSupply
        yield1d
        yield1w
        yield1m
        apy
        timestamp
      }
      yields: yields(order_by: { timestamp: desc }, limit: 20) {
        id
        profit
        timestamp
        dexPool {
          name
        }
      }
      vaultsPools {
      dexPools {
        address
        name
        tokenA {
          address
          decimals
          name
          symbol
        }
        tokenB {
          address
          decimals
          name
          symbol
        }
        }
      }
      executions {
        agentId
        decisionId
        hops
        profit
        routeDetails
        strategist
        transactionHash
        timestamp
      }
    }
  }
`

/**
 * Fetch all whitelisted DEX pools
 */
export const DEX_POOLS_QUERY = `
  query GetDexPools {
    dexPools: dexPools(where: { isWhitelisted: { _eq: true } }, order_by: { tvlUsd: desc }) {
      id
      address
      name
      tvlUsd
      tvlXtz
      lastUpdated
      tokenA {
        address
        symbol
        decimals
      }
      tokenB {
        address
        symbol
        decimals
      }
    }
  }
`

/**
 * Fetch user history (actions)
 */
export const USER_ACTIONS_QUERY = `
  query GetUserActions($user: String!, $vault: String, $limit: Int = 20) {
    userActions: userActions(
      where: { 
        user: { _eq: $user },
        _and: [
          { vaultId: { _ilike: $vault } }
        ]
      }, 
      order_by: { timestamp: desc }, 
      limit: $limit
    ) {
      id
      vaultId
      actionType
      assets
      shares
      timestamp
      transactionHash
    }
  }
`

/**
 * Fetch agent decisions (logs)
 */
export const AGENT_DECISIONS_QUERY = `
  query GetAgentDecisions($limit: Int = 20) {
    agentDecisions: agentDecisions(
      where: { 
        heuristicsVerdict: { _neq: "FAIL", _is_null: false },
        geminiVerdict: { _neq: "FAIL", _is_null: false }
      },
      order_by: { createdAt: desc }, 
      limit: $limit
    ) {
      id
      vaultId
      status
      heuristicsVerdict
      geminiVerdict
      opportunityDetails
      txHash
      error
      createdAt
    }
  }
`

/**
 * Fetch agent executions (arbitrage success)
 */
export const AGENT_EXECUTIONS_QUERY = `
  query GetAgentExecutions($limit: Int = 20) {
    agentExecutions: agentExecutions(order_by: { timestamp: desc }, limit: $limit) {
      id
      vaultId
      strategist
      hops
      routeDetails
      profit
      timestamp
      transactionHash
    }
  }
`

/**
 * Fetch agent by vault ID
 */
export const AGENT_BY_VAULT_QUERY = `
  query GetAgentByVault($vaultId: String!) {
    agents: agents(where: { vaultId: { _eq: $vaultId } }, limit: 1) {
      id
      name
      address
      details
      strategyConfig
    }
  }
`

/**
 * Fetch user portfolio statistics from the materialized view.
 * Includes net position (deposited - withdrawn), total shares, and lifetime rewards.
 */
export const USER_STATISTICS_QUERY = `
  query GetUserStatistics($address: String!, $vault: String = "%") {
    userStatistics(where: { 
      address: { _eq: $address },
      vaultAddress: { _ilike: $vault }
    }) {
      address
      vaultAddress
      totalDeposited
      totalWithdrawn
      netPosition
      totalShares
      totalRewardsEarned
      totalActions
      depositCount
      withdrawalCount
      firstActionAt
      lastActionAt
    }
  }
`
/**
 * Fetch the latest TVL and APY for a specific vault
 */
export const VAULT_TVL_QUERY = `
  query GetVaultTvl($address: String!) {
    vaultTvlLatest(where: { vaultAddress: { _eq: $address } }) {
      apy
      currentTvl
      lastUpdated
      totalSupply
      vaultAddress
      yield1d
    }
  }
`
