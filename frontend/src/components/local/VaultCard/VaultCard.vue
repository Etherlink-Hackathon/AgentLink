<script setup>
import { computed } from "vue"
import Badge from "@ui/Badge.vue"
import Tooltip from "@ui/Tooltip.vue"
import { getCurrencyIcon, getDexIcon } from "@utils/misc"
import { abbreviateNumber, toFix } from "@utils/amounts"
import { verifiedMakers, NETWORK_TYPE, chainConfig } from "~/services/config"
import Icon from "~/components/icons/Icon.vue"
import { currentNetwork } from "@sdk"

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

</script>

<template>
	<router-link :to="`/vaults/${vault.id}`" :class="$style.wrapper">
		<div :class="$style.header">
			<div :class="$style.symbol_imgs">
				<Tooltip placement="bottom-end">
					<Icon
						v-if="verifiedMakers[NETWORK_TYPE].includes(vault.creator)"
						name="logo_symbol"
						viewBox="0 0 100 100"
						alt="logo"
						:class="$style.logo_symbol"
					/>
					<template #content>Created by AgentLink</template>
				</Tooltip>
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
				{{ vault.strategyType }}
			</span>
		</div>

		<div :class="$style.description">
			<Icon name="coins" size="12" :class="$style.pool_icon" />
			<Tooltip placement="top">
				<div :class="$style.pool_icons">
					<div
						v-for="pool in vault.vaultsPools.slice(0, 4)"
						:key="pool.dexPools.address"
						:class="$style.pool_icon_item"
					>
						<img :src="getDexIcon(pool.dexPools.name)" :class="$style.dex_img" />
					</div>

					<div v-if="vault.vaultsPools.length > 4" :class="$style.more_indicator">...</div>
				</div>

				<template #content>
					<div :class="$style.tooltip_content">
						Number of arbitrage pools: {{ vault.vaultsPools.length }}
					</div>
				</template>
			</Tooltip>
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
				<span :class="$style.footer_value">{{ abbreviateNumber(vault.tvl) }} {{ chainConfig[currentNetwork.value]?.nativeCurrency?.symbol || 'ꜩ' }}</span>
			</Flex>
			<Flex direction="column" gap="4">
				<span :class="$style.footer_label">EST. REVENUE (24H)</span>
				<span :class="$style.footer_value">{{ (toFix(vault.revenue, 2)) }} {{ chainConfig[currentNetwork.value]?.nativeCurrency?.symbol || 'ꜩ' }}</span>
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

.logo_symbol {
	width: 30px;
	height: 30px;
	background: var(--app-bg);
	border-radius: 50%;
	border: 3px solid var(--card-bg);
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

.pool_icons {
	display: flex;
	align-items: center;
}

.pool_icon_item {
	display: flex;
	align-items: center;
	margin-right: -4px;
}

.dex_img {
	width: 20px;
	height: 20px;
	border-radius: 50%;
	background: var(--app-bg);
	border: 2px solid var(--card-bg);
	object-fit: contain;
}

.more_indicator {
	width: 20px;
	height: 20px;
	border-radius: 50%;
	background: var(--app-bg);
	border: 2px solid var(--card-bg);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 10px;
	font-weight: 800;
	color: var(--text-tertiary);
}

.tooltip_content {
	font-size: 12px;
	font-weight: 700;
	color: var(--text-primary);
}

.pool_icon {
	fill: var(--brand);
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
