-- =============================================================================
-- Vault TVL History (Materialized)
-- Tracks the Total Value Locked (TVL) of each vault over time using
-- VaultSnapshot records.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS vault_tvl_history;

CREATE MATERIALIZED VIEW vault_tvl_history AS
SELECT
    vault_id               AS vault_address,
    timestamp,
    total_assets           AS cumulative_tvl,
    total_supply           AS cumulative_supply,
    apy,
    yield_1d,
    -- Buckets for chart aggregation
    DATE_TRUNC('day', timestamp)   AS day_bucket,
    DATE_TRUNC('week', timestamp)  AS week_bucket,
    DATE_TRUNC('month', timestamp) AS month_bucket
FROM vault_snapshots
ORDER BY vault_id, timestamp;

CREATE UNIQUE INDEX IF NOT EXISTS idx_vault_tvl_history_id ON vault_tvl_history (vault_address, timestamp);


-- =============================================================================
-- Vault TVL Summary (Materialized) — Latest snapshot per vault
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS vault_tvl_latest;

CREATE MATERIALIZED VIEW vault_tvl_latest AS
SELECT DISTINCT ON (vault_id)
    vault_id  AS vault_address,
    timestamp AS last_updated,
    total_assets AS current_tvl,
    total_supply,
    apy,
    yield_1d
FROM vault_snapshots
ORDER BY vault_id, timestamp DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_vault_tvl_latest_address ON vault_tvl_latest (vault_address);
