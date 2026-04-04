-- =============================================================================
-- Vault TVL History (Materialized)
-- Tracks the Total Value Locked (TVL) of each vault over time using
-- UserTVL snapshots.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS vault_tvl_history;

CREATE MATERIALIZED VIEW vault_tvl_history AS
WITH delta_events AS (
    -- Each user action contributes a signed net change to vault TVL
    SELECT
        vault_id,
        timestamp,
        CASE
            WHEN action_type = 'DEPOSIT'  THEN  total_assets
            WHEN action_type = 'WITHDRAW' THEN -total_assets
            ELSE 0
        END AS tvl_delta
    FROM user_tvl
),
vault_events AS (
    SELECT
        vault_id,
        timestamp,
        SUM(tvl_delta) AS net_change
    FROM delta_events
    GROUP BY vault_id, timestamp
)
SELECT
    vault_id               AS vault_address,
    timestamp,
    net_change,
    -- Running cumulative TVL (clamped to 0 to avoid negatives on reindex)
    GREATEST(
        SUM(net_change) OVER (
            PARTITION BY vault_id
            ORDER BY timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        0
    ) AS cumulative_tvl,
    -- Buckets for chart aggregation
    DATE_TRUNC('day', timestamp)   AS day_bucket,
    DATE_TRUNC('week', timestamp)  AS week_bucket,
    DATE_TRUNC('month', timestamp) AS month_bucket
FROM vault_events
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
    -- Take the cumulative TVL at the most recent event for this vault
    GREATEST(
        SUM(
            CASE
                WHEN action_type = 'DEPOSIT'  THEN  total_assets
                WHEN action_type = 'WITHDRAW' THEN -total_assets
                ELSE 0
            END
        ) OVER (PARTITION BY vault_id ORDER BY timestamp),
        0
    ) AS current_tvl
FROM user_tvl
ORDER BY vault_id, timestamp DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_vault_tvl_latest_address ON vault_tvl_latest (vault_address);
