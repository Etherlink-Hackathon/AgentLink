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
| **Frontend** | `/frontend` | Sleek React + Vite Web3 UI for users to deposit XTZ/USDC and monitor their yield. |
| **Contracts** | `/contracts` | ERC-4626 Vault solidity contract ensuring capital safety and strictly enforcing the AI's "Strategist" boundaries. |
| **Backend** | `/backend` | The OpenClaw AI Agent running continuously, dynamically finding token spreads and piping rebalance transactions back to the vault. |

---

## Technical Flow

1. **User Deposit**: User visits the Frontend, connects wallet, and deposits `USDC` into `ArbitrageVault.sol`. They receive `arbUSDC` shares.
2. **Pool Discovery**: The Backend agent regularly polls Blockscout and GeckoTerminal for dynamic liquidity across the Etherlink L2 network.
3. **Execution**: The Agent identifies a mispricing (e.g. USDC/WXTZ on DexA vs DexB). 
4. **Strategist Action**: The Agent builds a transaction targeting `ArbitrageVault.executeArbitrage()` and signs it using its strictly limited Strategist wallet.
5. **On-Chain Enforcement**: The Vault contract executes the trade, reverting if the net balance of the vault doesn't grow.
6. **Yield**: The user's `arbUSDC` shares passively accrue value from the arbitrage profits.

---

## Getting Started

### 1. Backend (The AI Agent)
Requires `etherlink-mcp-server` to be running.
```bash
cd backend
npm install
cp .env.example .env
npm start
```

### 2. Frontend (The Yield Dashboard)
```bash
cd frontend
npm install
npm run dev
```

### 3. Contracts
```bash
cd contracts
# Standard Hardhat or Foundry commands to test/deploy the vault
```

---

## License

MIT