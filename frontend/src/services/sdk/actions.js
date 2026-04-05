import { markRaw } from "vue"
import { ethers } from "ethers"
import { flameWager } from "./flameWager"
import ERC20ABI from "@/abis/ERC20.json"

/**
 * Get an ERC20 contract instance
 */
export const getERC20Contract = (address) => {
  if (!flameWager.signer) throw new Error("SDK not initialized with signer")
  return new ethers.Contract(address, ERC20ABI, flameWager.signer)
}

/**
 * Get token allowance for a vault
 */
export const getAllowance = async (vaultAddress, ownerAddress) => {
  try {
    const vault = flameWager.vaults[vaultAddress.toLowerCase()]
    if (!vault) throw new Error("Vault contract not found for address: " + vaultAddress)
    const assetAddress = await vault.asset()
    const asset = getERC20Contract(assetAddress)
    return await asset.allowance(ownerAddress, vaultAddress)
  } catch (error) {
    console.error("Failed to get allowance:", error)
    throw error
  }
}

/**
 * Approve vault to spend assets
 */
export const approve = async (vaultAddress, amount) => {
  try {
    const vault = flameWager.vaults[vaultAddress.toLowerCase()]
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

/**
 * Read the user's current vault share balance (ERC-4626)
 */
export const getUserShares = async (vaultAddress, userAddress) => {
  try {
    const vault = flameWager.vaults[vaultAddress.toLowerCase()]
    if (!vault) throw new Error("Vault contract not found: " + vaultAddress)
    return await vault.balanceOf(userAddress)
  } catch (error) {
    console.error("Failed to get user shares:", error)
    throw error
  }
}

/**
 * Redeem vault shares for underlying assets (ERC-4626 redeem).
 */
export const redeem = async (vaultAddress, sharesAmount, receiver) => {
  try {
    const vault = flameWager.vaults[vaultAddress.toLowerCase()]
    if (!vault) throw new Error("Vault contract not found: " + vaultAddress)
    if (!flameWager.address) throw new Error("Wallet not connected")

    console.log(`Redeeming ${sharesAmount.toString()} shares from vault ${vaultAddress} for ${receiver}...`)
    const tx = await vault.redeem(sharesAmount, receiver, flameWager.address)
    return tx
  } catch (error) {
    console.error("Failed to redeem shares:", error)
    throw error
  }
}

/**
 * Withdraw underlying assets from the vault (ERC-4626 withdraw).
 */
export const withdrawAssets = async (vaultAddress, assetsAmount, receiver) => {
  try {
    const vault = flameWager.vaults[vaultAddress.toLowerCase()]
    if (!vault) throw new Error("Vault contract not found: " + vaultAddress)
    if (!flameWager.address) throw new Error("Wallet not connected")

    console.log(`Withdrawing ${assetsAmount.toString()} assets from vault ${vaultAddress} for ${receiver}...`)
    const tx = await vault.withdraw(assetsAmount, receiver, flameWager.address)
    return tx
  } catch (error) {
    console.error("Failed to withdraw assets:", error)
    throw error
  }
}
