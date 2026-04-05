import { createClient, cacheExchange, fetchExchange, subscriptionExchange } from "@urql/core"
import { createClient as createWSClient } from "graphql-ws"
import { computed, reactive, markRaw } from "vue"
import { ethers } from "ethers"
import { activeRpcNode, NETWORK_TYPE, activeChainConfig, dipdup, contracts } from "@config"
import vaultABI from "@/abis/ArbitrageVault.json"
import { Networks } from "@/services/constants/networks"

const flameWager = reactive({
  provider: null,
  signer: null,
  address: null,
  network: NETWORK_TYPE,
  chainId: activeRpcNode.chainId,
  isConnected: false,
  vaults: {},
})

const currentNetwork = computed(() => {
  return activeChainConfig.network
})

/**
 * Get contract addresses for current network
 */
const getContractAddresses = () => {
  const networkKey = currentNetwork.value === 'mainnet' ? 'mainnet' : 'testnet'
  return contracts[networkKey] || contracts.testnet
}

/**
 * Initialize GraphQL client
 */
const init = () => {
  const networkKey = currentNetwork.value === 'mainnet' ? 'mainnet' : 'testnet'
  const graphqlConfig = dipdup[networkKey]
  const addresses = getContractAddresses()

  // Only init contract if signer is available
  if (addresses.vault && flameWager.signer) {
    flameWager.vaults[addresses.vault.toLowerCase()] = markRaw(new ethers.Contract(
      addresses.vault,
      vaultABI,
      flameWager.signer
    ))
  }

  if (!graphqlConfig) {
    console.warn("GraphQL configuration not found for network:", networkKey)
    return
  }

  try {
    const wsClient = createWSClient({
      url: graphqlConfig.ws,
    });

    flameWager.gql = markRaw(createClient({
      url: graphqlConfig.graphql,
      exchanges: [
        cacheExchange,
        subscriptionExchange({
          forwardSubscription: (request) => {
            const input = { ...request, query: request.query || '' }
            return {
              subscribe: (sink) => {
                const unsubscribe = wsClient.subscribe(input, sink)
                return { unsubscribe }
              },
            }
          },
        }),
        fetchExchange,
      ],
      preferGetMethod: false,
      fetchOptions: {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      },
    }));

    console.log("✅ GraphQL client initialized:", graphqlConfig.graphql)
  } catch (error) {
    console.error("Failed to initialize GraphQL client:", error)
    flameWager.gql = markRaw(createClient({
      url: graphqlConfig.graphql,
      exchanges: [cacheExchange, fetchExchange],
    }))
  }
}

// Set default network from environment
if (typeof localStorage !== 'undefined') {
  localStorage.activeNetwork = localStorage.activeNetwork || NETWORK_TYPE;
  if (![Networks.MAINNET, Networks.TESTNET].includes(localStorage.activeNetwork)) {
    localStorage.activeNetwork = NETWORK_TYPE;
  }
}

/**
 * Initialize vault contracts
 */
const initVaults = (vaults) => {
  vaults.forEach(vault => {
    if (flameWager.signer) {
      flameWager.vaults[vault.address.toLowerCase()] = markRaw(new ethers.Contract(
        vault.address,
        vaultABI,
        flameWager.signer
      ))
    }
  })
}

/**
 * Initialize SDK with an external signer
 */
const initWithSigner = async (signer, address) => {
  if (!signer) throw new Error("Signer is required")

  try {
    flameWager.signer = markRaw(signer)
    flameWager.provider = markRaw(signer.provider)
    flameWager.address = address
    flameWager.isConnected = true

    const addresses = getContractAddresses()
    if (addresses.vault) {
      flameWager.vaults[addresses.vault.toLowerCase()] = markRaw(new ethers.Contract(
        addresses.vault,
        vaultABI,
        flameWager.signer
      ))
    }
    console.log("✅ AgentLink SDK connected to signer:", address)
  } catch (error) {
    console.error("Failed to initialize SDK with signer:", error)
    throw error
  }
}

const switchNetwork = async (network, router) => {
  if (![Networks.MAINNET, Networks.TESTNET].includes(network)) return
  localStorage.activeNetwork = network
  if (router) router.push("/")
}

const destroySubscription = (sub) => {
  if (sub && typeof sub.unsubscribe === 'function' && !sub.closed) {
    sub.unsubscribe()
  }
}

init()

export {
  flameWager,
  currentNetwork,
  switchNetwork,
  destroySubscription,
  getContractAddresses,
  initWithSigner,
  initVaults,
  init
}
