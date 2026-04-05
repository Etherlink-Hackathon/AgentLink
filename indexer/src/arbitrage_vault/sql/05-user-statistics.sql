-- =============================================================================
-- User Portfolio Statistics (Materialized)
-- Provides a per-address summary of deposit/withdrawal activity and net position.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS user_statistics;

CREATE MATERIALIZED VIEW user_statistics AS
WITH actions_agg AS (
    SELECT
        "user" AS address,
        vault_id AS vault_address,
        COALESCE(SUM(assets) FILTER (WHERE action_type = 'DEPOSIT'), 0) AS total_deposited,
        COALESCE(SUM(assets) FILTER (WHERE action_type = 'WITHDRAW'), 0) AS total_withdrawn,
        -- Net shares currently held in this specific vault
        COALESCE(SUM(shares) FILTER (WHERE action_type = 'DEPOSIT'), 0) - 
        COALESCE(SUM(shares) FILTER (WHERE action_type = 'WITHDRAW'), 0) AS net_shares,
        MIN(timestamp) AS first_action_at,
        MAX(timestamp) AS last_action_at,
        COUNT(*) AS total_actions,
        COUNT(*) FILTER (WHERE action_type = 'DEPOSIT') AS deposit_count,
        COUNT(*) FILTER (WHERE action_type = 'WITHDRAW') AS withdrawal_count
    FROM user_actions
    GROUP BY "user", vault_id
),
rewards_agg AS (
    SELECT
        user_id AS address,
        vault_id AS vault_address,
        COALESCE(SUM(reward_assets), 0) AS total_rewards_earned
    FROM user_rewards
    GROUP BY user_id, vault_id
)
SELECT
    a.address,
    a.vault_address,
    a.total_deposited,
    a.total_withdrawn,
    GREATEST(a.total_deposited - a.total_withdrawn, 0) AS net_position,
    a.net_shares AS total_shares,
    a.first_action_at,
    a.last_action_at,
    COALESCE(r.total_rewards_earned, 0) AS total_rewards_earned,
    a.total_actions,
    a.deposit_count,
    a.withdrawal_count
FROM actions_agg a
LEFT JOIN rewards_agg r ON a.address = r.address AND a.vault_address = r.vault_address;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_statistics_address_vault ON user_statistics (address, vault_address);
