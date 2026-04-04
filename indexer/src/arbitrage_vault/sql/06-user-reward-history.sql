-- =============================================================================
-- User Reward History (Materialized)
-- Powers the "Rewards Over Time" chart for a user.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS user_reward_history;

CREATE MATERIALIZED VIEW user_reward_history AS
SELECT
    r.id,
    r.user_id                       AS user_address,
    r.vault_id                      AS vault_address,
    r.execution_id,
    r.share_ratio,
    r.reward_assets,
    r.timestamp,
    -- Cumulative rewards up to this point (for a running-total chart line)
    SUM(r.reward_assets) OVER (
        PARTITION BY r.user_id, r.vault_id
        ORDER BY r.timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_rewards,
    -- Execution context for tooltip / detail view
    ae.profit                       AS execution_profit,
    ae.hops                         AS execution_hops,
    ae.transaction_hash             AS execution_tx_hash,
    -- Truncated time bucketing for chart aggregation in the frontend
    DATE_TRUNC('day', r.timestamp)  AS day_bucket,
    DATE_TRUNC('week', r.timestamp) AS week_bucket,
    DATE_TRUNC('month', r.timestamp) AS month_bucket
FROM user_rewards r
JOIN agent_executions ae ON r.execution_id = ae.id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_reward_history_id ON user_reward_history (id);


-- =============================================================================
-- Pre-aggregated reward summaries per user per vault (Materialized)
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS user_reward_summary;

CREATE MATERIALIZED VIEW user_reward_summary AS
SELECT
    r.user_id     AS user_address,
    r.vault_id    AS vault_address,
    -- 1-day window
    COALESCE(SUM(r.reward_assets) FILTER (
        WHERE r.timestamp >= NOW() - INTERVAL '1 day'
    ), 0) AS rewards_1d,
    -- 1-week window
    COALESCE(SUM(r.reward_assets) FILTER (
        WHERE r.timestamp >= NOW() - INTERVAL '7 days'
    ), 0) AS rewards_1w,
    -- 1-month window
    COALESCE(SUM(r.reward_assets) FILTER (
        WHERE r.timestamp >= NOW() - INTERVAL '30 days'
    ), 0) AS rewards_1mo,
    -- All-time totals
    COALESCE(SUM(r.reward_assets), 0)   AS rewards_all_time,
    COUNT(r.id)                          AS reward_events,
    MIN(r.timestamp)                     AS first_reward_at,
    MAX(r.timestamp)                     AS last_reward_at
FROM user_rewards r
GROUP BY r.user_id, r.vault_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_reward_summary_address ON user_reward_summary (user_address, vault_address);
