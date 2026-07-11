# Atlas project instructions

## Mission

This repository is being evolved from the AgentLink hackathon template into **Atlas**, an Etherlink-native product for Morpho Earn and, later, carefully bounded leveraged stXTZ strategies.

Preserve the working template while migrating incrementally. Do not perform broad renames or replace working subsystems unless the active task explicitly requires it.

## Current repository layout

- `frontend/`: Vue 3 + Vite dashboard using Pinia, wagmi, viem, and ethers.
- `contracts/`: Hardhat + Solidity 0.8.20 contracts and tests.
- `indexer/`: DipDup/Python indexer and agent services backed by PostgreSQL/Hasura.
- `docs/`: architecture, risk, security, and task documentation.

The existing arbitrage vault and Gemini agent are legacy template components. Treat them as reference implementations until an Atlas task explicitly migrates or removes them.

## Source of truth

Before implementing non-trivial work:

1. Read the relevant file under `docs/tasks/`.
2. Inspect the current implementation and tests.
3. State assumptions and produce a short implementation plan.
4. Map each acceptance criterion to a test or direct evidence.
5. Only then modify files.

Do not silently change product scope. Record architectural decisions in `docs/decisions/` when a change affects protocol design, trust assumptions, user funds, or cross-component interfaces.

## Engineering workflow

- Keep one task per branch and one coherent concern per pull request.
- Prefer small, reversible changes over repository-wide rewrites.
- Reproduce bugs through the user-facing or integration path before patching them.
- Add or update tests with implementation changes.
- Run the narrowest relevant checks during development, then the full component checks before completion.
- Use a fresh Codex context or `/review` for adversarial review before opening a pull request.
- Report commands run, results, residual risks, and unverified assumptions.

## Security boundaries

This is DeFi software. Never:

- expose, print, commit, or request production private keys, seed phrases, API secrets, or multisig credentials;
- submit mainnet transactions or deploy contracts unless the user explicitly requests that exact action;
- invent contract addresses, token decimals, market IDs, oracle configurations, LLTVs, router addresses, or liquidity assumptions;
- weaken authorization, slippage, deadline, health-factor, callback-sender, reentrancy, or asset-flow checks to make tests pass;
- give an AI agent unrestricted custody or arbitrary-call capability;
- describe an unverified strategy as safe, guaranteed, or risk-free.

Any code touching user funds, approvals, Morpho callbacks, swaps, oracle prices, debt accounting, or deployment is high risk and requires explicit tests plus human diff review.

## Validation commands

Frontend:

```bash
cd frontend
npm ci
npm run build
```

Contracts:

```bash
cd contracts
npm ci
npm run compile
npm test
```

Indexer/local infrastructure:

```bash
docker compose up -d db hasura
cd indexer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
dipdup run
```

On Windows PowerShell, activate the virtual environment with `venv\Scripts\Activate.ps1`.

## Definition of done

A task is complete only when:

- acceptance criteria are satisfied;
- relevant builds and tests pass;
- no secrets or generated artifacts are committed;
- user-facing states include loading, empty, error, disconnected-wallet, wrong-network, and transaction-pending behavior where applicable;
- protocol-facing changes document addresses, assumptions, and failure modes;
- the final report lists validation evidence and remaining risk.
