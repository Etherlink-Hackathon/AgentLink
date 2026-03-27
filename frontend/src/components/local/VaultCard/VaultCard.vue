<script setup>
import { computed } from "vue"
import Badge from "@ui/Badge.vue"
import Tooltip from "@ui/Tooltip.vue"
import { getCurrencyIcon } from "@utils/misc"
import { abbreviateNumber } from "@utils/amounts"

const props = defineProps({
	vault: { type: Object, required: true },
})

const statusColor = computed(() => {
	switch (props.vault.status?.toLowerCase()) {
		case "new": return "purple"
		case "active":
		case "running": return "yellow"
		case "finished": return "green"
		default: return "gray"
	}
})

// Mock participants for visual parity with FlameWager
const participants = [
  "tz1...", "tz1...", "tz1..."
]
</script>

<template>
	<router-link :to="`/vaults/${vault.id}`" :class="$style.wrapper">
		<div :class="$style.header">
			<div :class="$style.symbol_imgs">
				<img :src="getCurrencyIcon(vault.poolData?.token0?.symbol || 'ETH')" alt="symbol" />
				<img :src="getCurrencyIcon(vault.poolData?.token1?.symbol || 'USDC')" alt="symbol" />
			</div>

			<div :class="$style.users">
				<Tooltip placement="bottom-end">
					<div :class="$style.participants">
						<img
							:key="p"
							:src="`https://services.tzkt.io/v1/avatars/${p}`"
							:class="$style.user_avatar"
							alt="avatar"
						/>
					</div>
					<template #content>Participants: {{ vault.participants || 1 }}</template>
				</Tooltip>
			</div>
		</div>

		<div :class="$style.title">
			{{ vault.name }}
		</div>

		<div :class="$style.description">
			<span>
				<Icon name="price_event" size="12" :class="$style.strategy_icon" />
				Arbitrage Strategy
			</span>
			<div :class="$style.dot" />
			<span>{{ vault.poolData?.dex || 'Etherlink' }}</span>
		</div>

		<div :class="$style.badges">
			<Badge :color="statusColor" :class="$style.main_badge">
				<Icon :name="vault.status === 'new' ? 'event_new' : 'event_active'" size="12" />
				{{ vault.status?.toUpperCase() }}
			</Badge>

			<Badge color="red" :class="$style.badge">
				<Icon name="warning" size="12" />
				High Risk
			</Badge>
		</div>

		<div :class="$style.footer">
			<Flex direction="column" gap="4">
				<span :class="$style.footer_label">TVL</span>
				<span :class="$style.footer_value">${{ abbreviateNumber(vault.tvl) }}</span>
			</Flex>
			<Flex direction="column" gap="4">
				<span :class="$style.footer_label">EST. REVENUE (24H)</span>
				<span :class="$style.footer_value">${{ vault.revenue || '0.00' }}</span>
			</Flex>
			<Flex direction="column" align="end" gap="4">
				<span :class="$style.footer_label">APY</span>
				<span :class="[$style.footer_value, $style.green]">{{ vault.apy }}%</span>
			</Flex>
		</div>
	</router-link>
</template>

<style module>
.wrapper {
	display: block;
	background: var(--card-bg);
	border-radius: 8px;
	padding: 20px;
	transition: all 0.2s ease;
	text-decoration: none;
	border: 1px solid transparent;
}

.wrapper:hover {
	box-shadow: 0 0 0 2px var(--border);
}

.header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20px;
}

.symbol_imgs {
	position: relative;
	width: 34px;
	height: 34px;
}

.symbol_imgs img {
	width: 22px;
	height: 22px;
	border-radius: 5px;
}

.symbol_imgs img:first-child {
	position: absolute;
	z-index: 1;
	outline: 3px solid var(--card-bg);
	background: var(--card-bg);
}

.symbol_imgs img:last-child {
	position: absolute;
	bottom: 0;
	right: 0;
}

.users {
	display: flex;
	align-items: center;
}

.participants {
	display: flex;
}

.user_avatar {
	width: 30px;
	height: 30px;
	background: var(--app-bg);
	border-radius: 50%;
	border: 3px solid var(--card-bg);
	margin-left: -10px;
}

.title {
	font-size: 16px;
	font-weight: 700;
	color: var(--text-primary);
	margin-bottom: 8px;
}

.description {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 12px;
	font-weight: 600;
	color: var(--text-tertiary);
	margin-bottom: 20px;
}

.strategy_icon {
  fill: var(--brand);
}

.dot {
	width: 4px;
	height: 4px;
	border-radius: 50%;
	background: var(--opacity-20);
}

.badges {
	display: flex;
	gap: 8px;
	margin-bottom: 24px;
}

.main_badge {
	text-transform: capitalize;
}

.badge {
	background: var(--opacity-05);
}

.footer {
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
	padding-top: 16px;
	border-top: 1px solid var(--border);
}

.footer_label {
	font-size: 10px;
	font-weight: 700;
	color: var(--text-tertiary);
	letter-spacing: 0.05em;
}

.footer_value {
	font-size: 16px;
	font-weight: 700;
	color: var(--text-primary);
}

.green {
	color: var(--green);
}
</style>
