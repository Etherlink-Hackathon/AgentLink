# Task 0001 - Discover Morpho markets and vaults on Etherlink

## Status

Ready for planning

## User outcome

Atlas developers can run a deterministic read-only discovery process that identifies Morpho markets and MetaMorpho vaults on Etherlink and produces verified structured data for the frontend and later protocol work.

## Context

The AgentLink template currently uses an arbitrage vault and hard-coded frontend configuration. Atlas must not build deposit, borrow, or leveraged-position flows from guessed addresses or incomplete market assumptions.

The first implementation milestone is therefore a read-only Etherlink inventory. It should establish the on-chain facts needed by the frontend, contracts, indexer, and risk model.

## Scope

- Discover Morpho Blue markets from authoritative on-chain events and contract reads.
- Discover MetaMorpho vaults from the deployed factory and contract reads.
- Capture verified token metadata and chain identifiers.
- Capture market parameters and live state required for product feasibility analysis.
- Produce a machine-readable output that can later feed the Atlas frontend or indexer.
- Document how the output was generated and at which block.

## Non-goals

- Depositing, borrowing, repaying, withdrawing, or claiming rewards.
- Creating a market or vault.
- Implementing leveraged loops.
- Submitting mainnet transactions.
- Treating Morpho API support as available on Etherlink without verification.
- Replacing the existing AgentLink frontend or indexer in this task.

## Acceptance criteria

- [ ] The discovery process targets Etherlink mainnet chain ID `42793`.
- [ ] Morpho contract and factory addresses are configured in one explicit location with source references.
- [ ] Every discovered market includes market ID, loan token, collateral token, oracle, IRM, LLTV, total supply, total borrow, utilization, and available liquidity where derivable.
- [ ] Every discovered vault includes address, underlying asset, name, symbol, owner, curator, guardian/allocator roles where applicable, timelock, fee, queues/caps, total assets, and current allocations where derivable.
- [ ] Token addresses, symbols, decimals, and names are read on-chain and errors are represented explicitly.
- [ ] Output records chain ID, RPC endpoint label, block number, block timestamp, and generation timestamp.
- [ ] The process is read-only and does not require a private key.
- [ ] Re-running at the same block produces equivalent normalized output.
- [ ] RPC failures, malformed tokens, reverting contracts, and unsupported vault versions do not silently produce valid-looking zero values.
- [ ] A sample output and command are documented.

## Technical constraints

- Prefer RPC and contract events/reads as the source of truth.
- Keep protocol addresses separate from UI components.
- Do not add a new database requirement for the initial discovery command.
- Use checksummed EVM addresses in human-readable output.
- Preserve integer values as strings in JSON where JavaScript number precision would be unsafe.
- Make the design extensible for later persistence in DipDup/PostgreSQL.

## Security and risk

- Incorrect protocol addresses could cause all later work to target the wrong contracts.
- Token metadata calls may revert or return malformed values.
- Oracle presence does not establish oracle safety; discovery must not label a market safe.
- Available liquidity and rates are time-dependent and must include observation metadata.
- Do not log or request private keys.

## Validation plan

| Acceptance criterion | Test or evidence |
| --- | --- |
| Correct network and addresses | Unit/config test plus documented source |
| Deterministic normalized output | Fixture test using a fixed block or mocked RPC responses |
| Market fields | Schema test and comparison against direct contract reads |
| Vault fields | Schema test and comparison against direct contract reads |
| Error handling | Tests for revert, timeout, malformed metadata, and unknown version |
| Read-only behavior | Code review showing no signer/write client and execution without a key |
| Reproducible operation | Documented command and committed sample output |

## Required commands

To be finalized by the implementation plan. The final task must include component-specific tests and a repository-level reproducible command.

## Evidence

- Sample normalized JSON output.
- The block number used for verification.
- Logs or test output showing successful discovery.
- A short table of candidate Etherlink markets/vaults with no safety endorsement.

## Open decisions

- Whether the first implementation belongs in a new top-level `packages/discovery` module, under `indexer/`, or as a standalone script.
- Whether TypeScript/viem or Python/web3 is the preferred implementation language.
- Which vault versions are actually deployed and supported on Etherlink at implementation time.

## Completion report

- Changes made:
- Checks run and results:
- Evidence:
- Residual risks:
- Follow-up work:
