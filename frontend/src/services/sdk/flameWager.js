import { createClient, cacheExchange, fetchExchange, subscriptionExchange } from "@urql/core"
import { createClient as createWSClient } from "graphql-ws"
import { computed, reactive, markRaw } from "vue"
import { ethers } from "ethers"
import { switchChain } from "@wagmi/core"
import { activeRpcNode, NETWORK_TYPE, activeChainConfig, dipdup, contracts } from "@config"
import vaultABI from "@/abis/ArbitrageVault.json"
import { Networks } from "@/services/constants/networks"
import ERC20ABI from "@/abis/ERC20.json"

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
 * Get contract addresses for current network (placeholder)
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
    flameWager.vaults[addresses.vault] = markRaw(new ethers.Contract(
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
      // Ensure we are using standard fetchExchange without persisted queries
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
      // Explicitly set preferGetMethod to false if it was accidentally enabled elsewhere
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

    // Fallback: Create client without subscriptions
    flameWager.gql = markRaw(createClient({
      url: graphqlConfig.graphql,
      exchanges: [cacheExchange, fetchExchange],
    }))
  }
}

const getERC20Contract = (address) => {
  if (!flameWager.signer) throw new Error("SDK not initialized with signer")
  return new ethers.Contract(address, ERC20ABI, flameWager.signer)
}

const getAllowance = async (vaultAddress, ownerAddress) => {
  try {
    const vault = flameWager.vaults[vaultAddress]
    if (!vault) throw new Error("Vault contract not found for address: " + vaultAddress)
    const assetAddress = await vault.asset()
    const asset = getERC20Contract(assetAddress)
    return await asset.allowance(ownerAddress, vaultAddress)
  } catch (error) {
    console.error("Failed to get allowance:", error)
    throw error
  }
}

const approve = async (vaultAddress, amount) => {
  try {
    const vault = flameWager.vaults[vaultAddress]
    if (!vault) throw new Error("Vault contract not found for address: " + vaultAddress)
    const assetAddress = await vault.asset()
    const asset = getERC20Contract(assetAddress)

    console.log(`Approving ${amount.toString()} of ${assetAddress} for vault ${vaultAddress}...`)
    const tx = await asset.approve(vaultAddress, amount)
    return tx
  } catch (error) {
    console.error("Failed to approve asset:", error)
    throw error
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
 * Initialize SDK with an external signer (from wagmi/account store)
 * @param {ethers.Signer} signer - The signer from wagmi/ethers
 * @param {string} address - The connected wallet address
 */
const initWithSigner = async (signer, address) => {
  if (!signer) {
    throw new Error("Signer is required")
  }

  try {
    flameWager.signer = markRaw(signer)
    flameWager.provider = markRaw(signer.provider)
    flameWager.address = address
    flameWager.isConnected = true

    // Re-initialize contracts with the new signer
    const addresses = getContractAddresses()

    if (addresses.vault) {
      flameWager.vaults[addresses.vault] = markRaw(new ethers.Contract(
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

/**
 * Switch to a different network
 */
const switchNetwork = async (network, router) => {
  if (![Networks.MAINNET, Networks.TESTNET].includes(network)) return

  localStorage.activeNetwork = network

  if (router) {
    router.push("/")
  }
}

const destroySubscription = (sub) => {
  if (sub && typeof sub.unsubscribe === 'function' && !sub.closed) {
    sub.unsubscribe()
  }
}

// Initial call
init()

export {
  flameWager,
  currentNetwork,
  switchNetwork,
  destroySubscription,
  getContractAddresses,
  initWithSigner,
  initVaults,
  getAllowance,
  approve,
  init
}
