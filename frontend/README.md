# AgentLink — Sovereign Vault Dashboard

AgentLink is an advanced asset management platform built on **Etherlink**, designed for automated arbitrage and yield optimization. It leverages the **OpenClaw** architectural pattern to deploy institutional-grade arbitrage agents.

## Core Features

- **Sovereign Vaults**: Deploy capital into automated Cross-DEX arbitrage strategies.
- **Institutional Analytics**: Real-time yield visualization and performance tracking via ApexCharts.
- **Etherlink Integration**: Deeply integrated with Etherlink Mainnet and Shadownet, providing ultra-low latency execution logs.
- **Premium UI**: Built with a custom design system focused on transparency and security.

## Project Structure

- `src/api`: Backend service integrations for vault and pool discovery.
- `src/components/modules`: UI modules for Vault exploration and detail management.
- `src/services/sdk`: Lightweight SDK for Etherlink wallet and network management.
- `src/store`: Pinia stores for account and application state.

## Getting Started

### Prerequisites

- Node.js v18+
- MetaMask or any EIP-1193 compatible wallet
- Access to Etherlink Mainnet or Shadownet

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

### Configuration

Update `src/services/config.js` to configure RPC nodes, chain IDs, and contract addresses.

## Documentation

For more information on the underlying arbitrage logic, refer to the root `README.md` and `AGENT.md`.
