# Etherlink Omni-DEX Arbitrage Agent

## Overview

The **Etherlink Omni-DEX Arbitrage Agent** is a full-stack automated DeFi trading system powered by the [OpenClaw](https://openclaw.ai) framework and protected by an **ERC-4626 Vault**.

Instead of allowing an AI agent full control over user funds, this system uses a "Strategist" architecture:
1. Users deposit capital into a smart contract vault.
2. The agent automatically discovers real-time arbitrage loops across Etherlink DEXs (like Curve, Oku Trade, GeckoTerminal pools).
3. The agent calls the vault, which mathematically guarantees that the funds are never withdrawn to the agent, only passed through verified rebalancing operations.

---

## Architecure 

This is a modern Monorepo with three core components:

| Component | Path | Description |
| ---- | ---- | ---- |
| **Frontend** | `/frontend` | Sleek Vite + Vue Web3 dashboard for users to deposit XTZ/USDC and monitor real-time arbitrage yield. |
| **Contracts** | `/contracts` | ERC-4626 Vault solidity contract ensuring capital safety and strictly enforcing the AI strategist's boundaries. |
| **Backend** | `/backend` | OpenClaw AI Agent running on Node.js, dynamically discovering token spreads and executing rebalance transactions via the vault. |

---

## Technical Flow

1. **User Deposit**: Users connect their wallet to the Vue Dashboard and deposit `USDC` (or other supported assets) into the `ArbitrageVault`. The vault issues shares (`vUSDC`) representing their stake.
2. **Pool Discovery**: The Backend agent (Strategist) monitors Etherlink DEXs (V3Swap, EtherlinkDex, etc.) for price discrepancies using GeckoTerminal and on-chain data.
3. **Execution**: When a profitable loop is found, the Agent calls `executeArbitrage()` on the vault.
4. **On-Chain Enforcement**: 
    - The vault verifies the Strategist's signature.
    - The vault executes the swaps across whitelisted DEX routers.
    - **Mathematical Guard**: The transaction reverts if `finalAssets <= initialAssets`, ensuring the vault never loses money on a trade.
5. **Yield Accrual**: Profits remain in the vault, increasing the value of each share. Users can withdraw their principal and accrued yield at any time.

---

## Getting Started

### 1. Backend (The AI Agent)
Requires `etherlink-mcp-server` to be running.
```bash
cd backend
npm install
npm run dev
```

### 2. Frontend (The Yield Dashboard)
```bash
cd frontend
npm install
npm run dev
```

### 3. Contracts
Integrated with Hardhat for testing and deployment.
```bash
cd contracts
npx hardhat test
```

---

## Features
- **ERC-4626 Standard**: Full compatibility with DeFi protocols.
- **Strategist Role**: Strictly limited permissions for the AI agent.
- **Profit Enforcement**: Hardcoded requirement for net asset growth per trade.
- **Real-time Monitoring**: Dashboard with TVL, APY, and revenue stats.

---

## License

MIT