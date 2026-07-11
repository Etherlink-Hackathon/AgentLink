# Frontend instructions

These instructions extend the root `AGENTS.md` for work under `frontend/`.

## Stack and structure

- Vue 3 single-file components and JavaScript.
- Vite 4 build system.
- Pinia stores.
- wagmi/viem for wallet and EVM interactions; ethers is also present in legacy code.
- Vue Router routes are defined in `src/router/index.js`.
- Shared aliases are defined in `vite.config.js`.

Reuse the existing component system and visual language before adding new UI dependencies.

## Atlas migration rules

- Keep the existing app runnable while Atlas screens are introduced incrementally.
- Put protocol addresses and environment-dependent values in configuration modules or environment variables, not components.
- Separate read-only market/vault discovery from transaction execution.
- Do not display mock APY, TVL, health factor, rewards, or position values as live data.
- Clearly label estimated, indexed, stale, unavailable, and on-chain values.
- Present Atlas Earn separately from leveraged Atlas Boost positions because their risk models differ.

## Web3 UX requirements

Every transaction flow must account for:

- disconnected wallet;
- unsupported/wrong network;
- token approval or permit;
- user rejection;
- pending transaction;
- reverted transaction;
- confirmation and state refresh;
- insufficient balance and insufficient liquidity;
- explicit slippage, deadline, and risk disclosure when relevant.

Never hide liquidation, oracle, curator, liquidity, or smart-contract risk behind a single APY number.

## Validation

Run:

```bash
npm ci
npm run build
```

For behavior changes, provide direct evidence such as a screenshot, browser recording, or reproducible manual test path. Do not claim success from a build alone.
