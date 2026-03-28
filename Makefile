# Etherlink Arbitrage Vault — Global Management

.PHONY: help install run-agent run-indexer clean

help: ## Show this help message
	@echo 'Usage: make [TARGET]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies for agent and indexer
	cd backend && npm install
	cd backend-indexer && pip install -r requirements.txt

run-agent: ## Start the TypeScript arbitrage agent
	cd backend && npm run dev

run-indexer: ## Start the DipDup indexer
	cd backend-indexer && dipdup run

clean: ## Clean audit/build artifacts
	rm -rf backend/dist backend/node_modules
	rm -rf backend-indexer/__pycache__
