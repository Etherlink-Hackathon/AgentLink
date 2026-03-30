# Etherlink Arbitrage Vault — Global Management

.PHONY: help install run-indexer run-frontend test-contracts clean

help: ## Show this help message
	@echo 'Usage: make [TARGET]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies for all sub-projects
	cd indexer && pip install -r requirements.txt
	cd frontend && npm install
	cd contracts && npm install

run-indexer: ## Start the DipDup indexer and Python Agent
	cd indexer && dipdup run

run-frontend: ## Start the Vue.js dashboard
	cd frontend && npm run dev

test-contracts: ## Run Hardhat tests for the vault contracts
	cd contracts && npm run test

clean: ## Clean build artifacts
	rm -rf frontend/dist frontend/node_modules
	rm -rf contracts/artifacts contracts/cache contracts/node_modules
	find indexer -name "__pycache__" -exec rm -rf {} +
