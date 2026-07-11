# Indexer and agent instructions

These instructions extend the root `AGENTS.md` for work under `indexer/`.

## Current state

The current DipDup package indexes the legacy `ArbitrageVault` and contains a Gemini-based arbitrage strategist. Treat it as a reference implementation while Atlas data ingestion is introduced separately.

Do not mix Morpho market/vault entities into arbitrage-specific models or handlers without an explicit migration plan.

## Atlas indexing principles

- On-chain RPC data is the source of truth for balances, positions, market parameters, and transaction status.
- Persist chain ID, contract address, block number, transaction hash, and log index for indexed entities.
- Make handlers idempotent and safe to replay.
- Handle chain reorganizations and duplicate events according to DipDup conventions.
- Separate raw indexed state from derived analytics such as APY, P&L, liquidation price, and risk labels.
- Record the calculation method and observation time for derived values.
- Do not silently substitute stale or mocked data for live protocol data.

## Agent safety

- The agent must not hold custody of user funds.
- Never load production private keys during tests or local development.
- Default execution services to dry-run/read-only mode.
- Any keeper or automation action must be bounded on-chain so a compromised process cannot redirect funds or increase risk outside user-approved limits.
- Log decisions and transaction simulation results without logging secrets.

## Local validation

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start dependencies from the repository root:

```bash
docker compose up -d db hasura
```

Then run:

```bash
dipdup run
```

For new Python modules, add focused tests where possible and at minimum run syntax/import checks on changed files. Document any validation that requires RPC, database, or API access and distinguish it from checks actually executed.
