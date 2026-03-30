AgentLink is architected with a "Security-First" approach, ensuring that all automated strategist operations are strictly bounded by smart contract logic and immutable roles.

## Strategist Boundaries

Unlike traditional trading bots, our Gemini-driven strategist operates within a strictly defined `STRATEGIST_ROLE`. This role is granted by the `ArbitrageVault` contract and cannot be escalated.

### What the Strategist CAN DO:
- **`executeArbitrage()`**: Trigger atomic trade paths on the vault.
- **Read State**: Request real-time reserve ratios and user balances.
- **Quote Swaps**: Simulate transaction outcomes to minimize slippage.

### What the Strategist CANNOT DO:
- **`withdraw()`**: It is programmatically impossible for the strategist to move capital out of the vault to an external EOA.
- **`deposit()`**: The strategist cannot mint new shares or adjust user balances.
- **`grantRole()`**: It has no administrative permissions over the contract's governance.

## Oracle Integration

We utilize **SupraOracles** on Etherlink for real-time asset pricing. This ensures the agent's internal arbitrage calculations are cross-verified against high-integrity price feeds, preventing "fat-finger" trades during extreme volatility.

## Smart Contract Audits

The `ArbitrageVault` is an ERC-4626 compliant contract. Our core logic is based on OpenZeppelin's audited standards, ensuring that accounting for shares and underlying assets is both gas-efficient and mathematically sound.

> [!IMPORTANT]
> All arbitrage transactions are **atomic**. If any step of the multi-pool trade path fails, the entire transaction reverts, ensuring capital safety for all depositors.
