Automated arbitrage involves several inherent risks that users should be aware of before committing capital to the `ArbitrageVault`.

## Arbitrage Risks

### Slippage & Front-Running
Despite our agent's calculations, high-volatility events can cause capital loss if the execution slippage exceeds the anticipated arbitrage spread. Additionally, "sandwich" attacks by MEV bots on the underlying DEXs can impact the net yield of the vault.

### Execution Failures
Arbitrage transactions involve multiple atomic steps across different protocol contracts. If any pool in the path experiences a technical failure or liquidity crunch, the transaction will revert, causing gas fees to be spent without a profit.

## Platform Risks

### Smart Contract Risk
While we use audited OpenZeppelin standards, all smart contracts are subject to potential bug discoveries in the underlying protocol code (Curve, Uniswap, etc.).

### Decentralized Oracle Dependency
Our agent relies on the **SupraOracles** feed for pricing. Any delay or inaccuracy in the oracle data could lead the agent to initiate unprofitable trade paths.

### DEX Liquidity
If the liquidity depth of a monitored pool (see [Available DEX Pools](file:///home/huydq/AgentLink/DEX_POOLS.md)) drops significantly, the agent's ability to execute large trades will be restricted, reducing the vault's total potential yield.

> [!WARNING]
> Yields are **not guaranteed**. Arbitrage opportunities depend on market imbalances across DEXs. Periods of high correlation between tokens may lead to lower yield performance.
