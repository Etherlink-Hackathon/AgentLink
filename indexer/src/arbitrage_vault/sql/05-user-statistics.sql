-- =============================================================================
-- User Portfolio Statistics (Materialized)
-- Provides a per-address summary of deposit/withdrawal activity and net position.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS user_statistics;

CREATE MATERIALIZED VIEW user_statistics AS
SELECT
    u.address,
    u.total_deposited,
    u.total_withdrawn,
    -- Net current position (assets still in vaults)
    GREATEST(u.total_deposited - u.total_withdrawn, 0) AS net_position,
    u.total_shares,
    u.first_action_at,
    u.last_action_at,
    -- Total lifetime rewards earned across all vaults
    COALESCE(SUM(r.reward_assets), 0) AS total_rewards_earned,
    -- Number of distinct vaults the user has interacted with
    COUNT(DISTINCT ua.vault_id) AS vaults_participated,
    -- Total number of deposit/withdraw events
    COUNT(ua.id) AS total_actions,
    COUNT(ua.id) FILTER (WHERE ua.action_type = 'DEPOSIT') AS deposit_count,
    COUNT(ua.id) FILTER (WHERE ua.action_type = 'WITHDRAW') AS withdrawal_count
FROM users u
LEFT JOIN user_actions ua ON u.address = ua.user
LEFT JOIN user_rewards r ON u.address = r.user_id
GROUP BY u.address, u.total_deposited, u.total_withdrawn, u.total_shares,
         u.first_action_at, u.last_action_at;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_statistics_address ON user_statistics (address);
