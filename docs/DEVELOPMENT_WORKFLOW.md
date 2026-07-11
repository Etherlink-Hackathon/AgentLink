# Atlas development workflow

This workflow uses **Antigravity IDE** as the main editor and **Codex CLI** inside Antigravity's integrated terminal. No separate terminal emulator or editor is required.

## 1. Open and prepare the repository

```bash
git clone https://github.com/Etherlink-Hackathon/AgentLink.git
cd AgentLink
git checkout main
git pull --ff-only
```

Open the repository root in Antigravity so Codex can read the root and nested `AGENTS.md` files.

Install component dependencies:

```bash
cd frontend && npm ci && cd ..
cd contracts && npm ci && cd ..
```

For the indexer:

```bash
cd indexer
python -m venv venv
```

Activate the virtual environment:

```powershell
# PowerShell
venv\Scripts\Activate.ps1
```

```bash
# Linux/WSL/macOS
source venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
cd ..
```

Copy local environment examples before running services:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Do not put real production credentials in tracked files.

## 2. Use one branch per task

```bash
git checkout main
git pull --ff-only
git checkout -b agent/<short-task-name>
```

For two genuinely independent tasks, use Git worktrees rather than running agents in the same directory:

```bash
git worktree add ../AgentLink-<task> -b agent/<task> main
```

Start with one Codex implementation session at a time. Add parallel sessions only after CI and task boundaries are reliable.

## 3. Create a task brief

Copy `docs/tasks/TEMPLATE.md` to a numbered task file. Define:

- user outcome;
- scope and non-goals;
- acceptance criteria;
- security and protocol assumptions;
- validation plan;
- required evidence.

A task should be independently reviewable and usually fit in one pull request.

## 4. Planning prompt

Start Codex from the repository root:

```bash
codex
```

Use this prompt before implementation:

```text
Read AGENTS.md and the relevant nested AGENTS.md files.
Read the active task document.
Inspect the existing implementation and tests.
Do not modify files yet.

Produce a concise implementation plan that:
- identifies affected components and interfaces;
- maps every acceptance criterion to a test or direct evidence;
- lists security and migration risks;
- calls out assumptions requiring verification;
- avoids unrelated refactoring.
```

Review the plan before asking Codex to implement.

## 5. Implementation prompt

```text
Implement the approved plan for the active task.
Stay within scope and preserve the existing working template.
Add or update tests with the implementation.
Run the narrowest relevant checks while working.
Do not deploy contracts, submit mainnet transactions, or use production credentials.
Stop and report if an unverified address, protocol assumption, or product decision blocks correctness.
```

Use Antigravity for code navigation, browser debugging, transaction traces, and focused diff review.

## 6. Validation

Frontend:

```bash
cd frontend
npm run build
```

Contracts:

```bash
cd contracts
npm run compile
npm test
```

Local infrastructure:

```bash
docker compose up -d db hasura
```

Record direct evidence for user-facing or protocol-facing behavior. Examples include screenshots, transaction simulations, fork-test traces, indexed event comparisons, and reproducible manual test steps.

## 7. Independent review

Use a fresh Codex session or `/review`:

```text
Review this branch as an adversarial senior DeFi engineer.
Evaluate it against the active task's acceptance criteria.
Prioritize incorrect behavior, fund-loss paths, authorization mistakes, callback validation, oracle assumptions, slippage, rounding, reentrancy, stale data, and hidden regressions.
Return findings by severity with exact file references.
Do not praise the code or summarize unchanged files.
```

Fix confirmed findings and rerun validation.

## 8. Pull request

Before opening a PR:

```bash
git status
git diff --check
git diff main...HEAD
```

The PR must state:

- what changed and why;
- acceptance criteria covered;
- checks actually run and their result;
- evidence produced;
- remaining risks and unverified assumptions;
- whether the change touches user funds or deployment.

Create high-risk contract and deployment PRs as drafts and require human diff review.

## Recommended first Atlas milestones

1. Inventory Morpho markets and MetaMorpho vaults deployed on Etherlink.
2. Add a read-only Atlas data layer and dashboard using verified addresses.
3. Integrate direct non-leveraged Earn deposit and redemption flows.
4. Build a threat model and fork-tested prototype for user-owned Atlas Boost positions.
5. Add bounded automation only after the manual open/close path is proven.
