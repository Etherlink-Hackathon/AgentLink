FROM dipdup/dipdup:8.2

USER root

# Install system dependencies for web3/psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER dipdup

# Install Python dependencies
COPY --chown=dipdup:dipdup requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY --chown=dipdup:dipdup . .

# Default command to run the indexer
CMD ["dipdup", "run"]
