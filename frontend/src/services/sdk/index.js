import {
  flameWager,
  switchNetwork,
  currentNetwork,
  destroySubscription,
  initWithSigner,
  getContractAddresses,
  initVaults,
} from "./flameWager"
import {
  approve,
  getAllowance,
  getUserShares,
  redeem,
  withdrawAssets,
  getERC20Contract,
} from "./actions"
import analytics from "./analytics"

/**
 * Utility function to fetch balance for a given address
 */
export async function fetchBalance(address) {
  const { getBalance } = await import("@wagmi/core")
  const { ethers } = await import("ethers")
  const { config, activeChainConfig } = await import("@config")

  if (!address) return "0"
  try {
    const balanceData = await getBalance(config, {
      address,
      chainId: activeChainConfig.id,
    })
    return ethers.formatEther(balanceData.value)
  } catch (error) {
    console.error("Error fetching balance:", error)
    return "0"
  }
}

export {
  flameWager,
  switchNetwork,
  currentNetwork,
  destroySubscription,
  getContractAddresses,
  initWithSigner,
  initVaults,
  analytics,
  approve,
  getAllowance,
  getUserShares,
  redeem,
  withdrawAssets,
  getERC20Contract,
}
