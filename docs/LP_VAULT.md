# Liquidity Provider (LP) Vault

The AgentLink LP Vault is a trustless, automated yield-generation engine built on the **ERC-4626 Tokenized Vault Standard**. It allows users to deposit capital and earn yield from sophisticated on-chain arbitrage strategies without relinquishing custody to an AI agent.

## ERC-4626: The Gold Standard

By utilizing the ERC-4626 standard, AgentLink ensures full composability with the broader EVM ecosystem. This means your vault shares (`vAssets`) can eventually be used as collateral or integrated into other DeFi protocols.

### Share-Based Accounting
When you deposit assets (e.g., `USDC`) into the vault, you are minted a proportional amount of shares. These shares represent your claim on the total pool of assets held by the vault.

- **Deposit**: `USDC` in -> `vUSDC` out.
- **Withdraw**: `vUSDC` in -> `USDC` (Principal + Yield) out.

## How Yield is Generated

The "Arbitrage Yield" is not based on inflation or secondary token rewards; it is generated from real market inefficiencies.

1. **Detection**: The AI Strategist identifies a price discrepancy between DEXs (e.g., Curve and Oku).
2. **Execution**: The vault executes an atomic multi-hop swap.
3. **Yield Collection**: The profit from the arbitrage loop is kept directly in the vault contract.
4. **Price Per Share (PPS)**: As the total assets in the vault increase from arbitrage profits, each existing share becomes worth more underlying assets.

### Mathematical Guarantee

The `ArbitrageVault` contract includes a strict on-chain check for every trade:

```solidity
uint256 finalAssets = totalAssets();
require(finalAssets > initialAssets, "Arbitrage: Negative Yield");
```

This ensures that the strategist can **never** execute a trade that results in a net loss for the vault. Every successful transaction directly increases the value of your LP shares.

> [!TIP]
> You can monitor your personal yield and the current **Price Per Share** directly in the [Vault Dashboard].
