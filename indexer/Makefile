# Etherlink Arbitrage Indexer — Management
.PHONY: help install run build clean

help: ## Show this help message
	@echo 'Usage: make [TARGET]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install python dependencies locally
	pip install -r requirements.txt

run: ## Start the DipDup indexer and background agent
	dipdup run

build: ## Build the docker image
	docker build -t etherlink-arbitrage-indexer .

clean: ## Remove temporary files
	rm -rf __pycache__ .pytest_cache
