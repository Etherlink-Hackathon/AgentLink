import { pipe, subscribe } from "wonka"
import { flameWager } from "@/services/sdk"
import { 
  AGENT_DECISIONS_QUERY, 
  AGENT_EXECUTIONS_QUERY, 
  VAULT_BY_ADDRESS_QUERY,
  VAULT_TVL_QUERY
} from "./queries"

/**
 * Common subscription handler
 */
const handleSubscription = (query, variables, onUpdate, transformFn = (data) => data) => {
  try {
    if (!flameWager.gql) {
      console.warn("GraphQL client not initialized")
      return { unsubscribe: () => {} }
    }

    const subQuery = query.replace(/query\s/, "subscription ")
    const { unsubscribe } = pipe(
      flameWager.gql.subscription(subQuery, variables),
      subscribe((result) => {
        if (result.error) {
          console.error("Subscription error:", result.error)
          return
        }

        if (result.data) {
          onUpdate(transformFn(result.data))
        }
      })
    )

    return { unsubscribe }
  } catch (error) {
    console.error("Failed to setup subscription:", error)
    return { unsubscribe: () => {} }
  }
}

/**
 * Subscribe to agent decisions (real-time logs)
 */
export const subscribeToAgentDecisions = (onUpdate) => {
  return handleSubscription(
    AGENT_DECISIONS_QUERY,
    { limit: 10 },
    onUpdate,
    (data) => data.agentDecisions
  )
}

/**
 * Subscribe to agent executions (real-time arbitrage)
 */
export const subscribeToAgentExecutions = (onUpdate) => {
  return handleSubscription(
    AGENT_EXECUTIONS_QUERY,
    { limit: 10 },
    onUpdate,
    (data) => data.agentExecutions
  )
}

/**
 * Subscribe to vault updates (APY/TVL)
 */
export const subscribeToVault = (address, onUpdate) => {
  return handleSubscription(
    VAULT_BY_ADDRESS_QUERY,
    { address },
    onUpdate,
    (data) => data.vault
  )
}
/**
 * Subscribe to real-time vault TVL updates
 */
export const subscribeToVaultTvl = (address, onUpdate) => {
  return handleSubscription(
    VAULT_TVL_QUERY,
    { address },
    onUpdate,
    (data) => data.vaultTvlLatest?.[0]
  )
}
