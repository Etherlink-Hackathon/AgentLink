# Etherlink Arbitrage Indexer & AI Agent (Soul)

A high-performance DipDup-based indexer for the Etherlink Arbitrage Vault, featuring a near-zero latency execution engine driven by Google Gemini and Mathematical Heuristics.

## 🚀 Architecture: The Cortex & The Soul

- **The Cortex (DipDup)**: Continuously monitors dex pools on Etherlink, computes triangular arbitrage opportunities, and emits execution signals.
- **The Soul (Gemini API)**: A high-speed strategic review engine that validates trades against market context, liquidity depth, and risk signals.
- **The Will (Agent Executor)**: A background listener that signs and broadcasts transactions using `web3.py`, enforcing sequential nonce management.

## 🛠 Setup & Configuration

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Google Gemini API Key

### Environment Variables
Create a `.env` file in the root directory:
```bash
# DipDup / Postgres
POSTGRES_PASSWORD=your_password
RPC_URL=https://node.mainnet.etherlink.com

# AI Strategist
GEMINI_API_KEY=your_gemini_api_key

# Execution
VAULT_ADDRESS=0x...
STRATEGIST_PRIVATE_KEY=your_private_key
STRATEGIST_ADDRESS=0x...
```

### Installation

1. **Clone and enter the project directory**:
   ```bash
   cd indexer
   ```

2. **Install dependencies**:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```
   
   Then 
   ```bash
   # With Poetry (recommended)
   poetry install
   
   # Or with pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Configure contract addresses**:
   Edit the appropriate `dipdup.{network}.yml` file with your deployed contract addresses.

### Running with Docker (Recommended)

1. **Start all services**:
```bash
   make docker-up
   # or
   docker-compose up -d
   ```

2. **Check logs**:
   ```bash
   make docker-logs
   # or
   docker-compose logs -f indexer
   ```

3. **Initialize database** (first time only):
```bash
   docker-compose exec indexer dipdup -c dipdup.yml init
   ```

4. **Schema Wipe / Reindexing** (if schema changes):
   If you need to wipe the database and reindex (e.g. after changing models or SQL views), run:
```bash
   docker-compose run --rm indexer -c dipdup.yml schema wipe --force
   ```

## 📖 How to Run

### Local Development
1. Install dependencies:
   ```bash
   make install
   ```
2. Start the indexer:
   ```bash
   make run
   ```

### Docker Deployment
1. Build the image:
   ```bash
   make build
   ```
2. Run with Docker Compose (ensure you have a `docker-compose.yml` for Postgres):
   ```bash
   docker-compose up -d
   ```

## 🧠 Strategic Logic
- **Math-First Fallback**: If Gemini rejects a trade but the mathematical heuristics show guaranteed profit, the trade **proceeds**.
- **1s Hard Timeout**: Gemini is given exactly one second to respond to maintain trade window viability.
- **Fast Gas Strategy**: Transactions are broadcast using "Fast" gas estimation from the node.
