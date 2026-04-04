-- Refresh all materialized views for the arbitrage dashboard
-- Using CONCURRENTLY to avoid locking the views during the refresh (requires UNIQUE INDEX)

REFRESH MATERIALIZED VIEW CONCURRENTLY user_statistics;
REFRESH MATERIALIZED VIEW CONCURRENTLY user_reward_history;
REFRESH MATERIALIZED VIEW CONCURRENTLY user_reward_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY vault_tvl_history;
REFRESH MATERIALIZED VIEW CONCURRENTLY vault_tvl_latest;
