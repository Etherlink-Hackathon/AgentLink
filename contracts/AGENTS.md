# Contract instructions

These instructions extend the root `AGENTS.md` for work under `contracts/`.

## Current state

The directory contains the legacy AgentLink ERC-4626 arbitrage vault, deployment scripts, and Hardhat tests. Preserve that implementation unless an active task explicitly migrates it.

New Atlas protocol work should be isolated from the legacy vault, preferably under a clearly named Atlas namespace or directory, until migration is intentionally completed.

## Contract standards

- Solidity version: 0.8.20 unless a task documents a justified upgrade.
- Use OpenZeppelin primitives where appropriate.
- Prefer narrowly scoped contracts with explicit asset-flow invariants.
- Use custom errors for new protocol code.
- Follow checks-effects-interactions and add reentrancy protection where external calls can affect funds.
- Avoid unbounded loops over user-controlled collections.
- Avoid upgradeability unless the task explicitly specifies the governance and migration model.

## Morpho integration requirements

For code interacting with Morpho:

- Verify the exact Etherlink deployment address and ABI from authoritative sources.
- Treat Earn vault deposits and leveraged borrow positions as different product surfaces.
- Validate callback callers and callback context; never accept arbitrary callback invocation.
- Prefer user-owned Morpho positions over pooled custody for the initial Atlas Boost implementation.
- Enforce market, token, router, and function allowlists.
- Enforce slippage, deadlines, minimum post-operation health factor, and dust refunds.
- Use share-based full repayment where rounding can otherwise leave residual debt.
- Do not add arbitrary external-call forwarding.

## Required tests for fund-moving changes

At minimum, test:

- authorization success and failure;
- unauthorized callback rejection;
- normal open/close or deposit/redeem path;
- slippage and deadline reverts;
- insufficient output and insufficient liquidity;
- rounding and dust behavior;
- reentrancy attempts;
- unsupported market/token/router rejection;
- health-factor boundary behavior;
- full rollback when any atomic step fails.

Use fork tests for deployed-protocol behavior when practical, but keep deterministic unit tests for local invariants.

## Validation

Run:

```bash
npm ci
npm run compile
npm test
```

Do not deploy or verify contracts as part of routine validation. Deployment requires an explicit user request and a separate review of network, addresses, signer, constructor arguments, and rollback plan.
