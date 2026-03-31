All core AgentLink contracts are deployed on the **Etherlink Mainnet**. This page serves as the official registry for verified contract addresses and their respective roles within the ecosystem.

## Core Protocol

### Arbitrage Vault (ERC-4626)
The primary entry point for Liquidity Providers. This contract manages user deposits, issues shares, and enforces the strategist's operational boundaries.

- **Address**: [`0x895Ea1c1A1EF1EceF0Fb822e33BE0bB9d493559d`](https://explorer.etherlink.com/address/0x895Ea1c1A1EF1EceF0Fb822e33BE0bB9d493559d)
- **Standard**: ERC-4626
- **Network**: Etherlink Mainnet (Chain ID: 42793)

## Infrastructure Dependencies

### SupraOracles
We utilize Supra's pull-based oracle architecture for real-time price validation.

- **Type**: Decentralized Price Feed
- **Usage**: Internal slippage calculation and profit enforcement.

### DEX Routers
The vault interacts with the following whitelisted routers to perform atomic arbitrage swaps:

| Platform | Role |
| :--- | :--- |
| **Curve** | Stableswap & Tri-Crypto Multi-Hops |
| **Oku Trade** | Uniswap v3 Concentrated Liquidity Swaps |

> [!NOTE]
> For security reasons, the Vault only interacts with verified and whitelisted DEX routers. The AI Strategist cannot add new routers without a governance-controlled role update.
