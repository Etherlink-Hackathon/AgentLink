/**
 * AgentLink SDK
 * Handles wallet connection and network state for the AgentLink frontend
 */

import { computed, reactive, markRaw } from "vue"
import { ethers } from "ethers"
import { switchChain } from "@wagmi/core"
import { activeRpcNode, NETWORK_TYPE, activeChainConfig } from "@config"

/**
 * Services.Constants
 */
import { Networks } from "@/services/constants/networks"

const flameWager = reactive({
  provider: null,
  signer: null,
  address: null,
  network: NETWORK_TYPE,
  chainId: activeRpcNode.chainId,
  isConnected: false,
})

const currentNetwork = computed(() => {
  return activeChainConfig.network
})

// Set default network from environment
if (typeof localStorage !== 'undefined') {
  localStorage.activeNetwork = localStorage.activeNetwork || NETWORK_TYPE;

  if (![Networks.MAINNET, Networks.TESTNET].includes(localStorage.activeNetwork)) {
    localStorage.activeNetwork = NETWORK_TYPE;
  }
}

/**
 * Get contract addresses for current network (placeholder)
 */
const getContractAddresses = () => {
  return {}
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

export {
  flameWager,
  currentNetwork,
  switchNetwork,
  destroySubscription,
  getContractAddresses,
  initWithSigner,
}
