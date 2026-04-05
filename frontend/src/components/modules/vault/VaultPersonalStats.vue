<script setup>
/**
 * Vendor
 */
import { computed } from "vue"

/**
 * Store
 */
import { useAccountStore } from "@store/account"

/**
 * Services
 */
import { abbreviateNumber, numberWithSymbol } from "@utils/amounts"

/**
 * UI
 */
import Tooltip from "@ui/Tooltip.vue"

const props = defineProps({
	vault: {
		type: Object,
		default: () => ({}),
	},
	position: {
		type: Object,
		default: null,
	},
})

const accountStore = useAccountStore()

// Net deposited position from indexer (historical)
const tvl = computed(() => {
	const raw = props.position?.redeemableAssets || "0"
	try {
		return parseFloat(raw) / 10 ** 18
	} catch {
		return 0
	}
})

// Live on-chain redeemable amount (what user actually gets back now)
const returning = computed(() => {
	const raw = props.position?.redeemableAssets || "0"
	try {
		return parseFloat(raw) / 10 ** 18
	} catch {
		return 0
	}
})

// Lifetime rewards credited from arbitrage executions
const potential = computed(() => {
	const raw = props.position?.totalRewardsEarned || "0"
	return parseFloat(raw)
})

const symbol = computed(() => props.vault?.assetSymbol || props.vault?.token1?.symbol || "XTZ")

</script>

<template>
	<div :class="$style.wrapper">
		<!-- TVL -->
		<div :class="$style.sector">
			<div :class="$style.base">
				<div :class="$style.name">MY TVL</div>

				<div :class="$style.amount">
					{{ abbreviateNumber(tvl) }}
					<span>{{ symbol }}</span>
				</div>
			</div>

			<Tooltip placement="bottom-start">
				<div :class="$style.icon">
					<Icon name="coins" size="20" color="tertiary"/>
				</div>

				<template #content> Your Total Deposits + Accrued Yield </template>
			</Tooltip>
		</div>


		<!-- Potential -->
		<div :class="$style.sector">
			<div :class="$style.base">
				<div :class="$style.name">EARNED</div>

				<div :class="$style.amount">
					{{ potential.toFixed(2) }} <span>{{ symbol }}</span>
				</div>
			</div>

			<Tooltip placement="bottom-start">
				<div :class="$style.icon">
					<Icon name="plus_circle" size="20" color="tertiary"/>
				</div>

				<template #content> Your Total Rewards </template>
			</Tooltip>
		</div>
	</div>

	<Flex align="center" gap="6" :class="$style.help_footer">
		<Icon name="help" size="14" color="tertiary" />
		<Flex>
			<Text size="12" height="16" weight="500" color="tertiary">
				<b>Returning & Potential</b> are estimates based on active arbitrage strategies.
			</Text>
		</Flex>
	</Flex>
</template>

<style module>
.wrapper {
	display: flex;
	align-items: center;
	gap: 18px;

	border-radius: 8px;
	background: var(--card-bg);

	padding: 0 20px;
	margin-bottom: 24px;
}

.sector {
	display: flex;
	align-items: center;
	justify-content: space-between;

	height: 84px;

	flex: 1;
}

.sector:nth-child(1){
	border-right: 2px solid rgba(255, 255, 255, 0.05);
	padding-right: 18px;
}

.base {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.name {
	font-size: 11px;
	line-height: 1.1;
	font-weight: 700;
	color: var(--text-tertiary);
	letter-spacing: 0.05em;
}

.amount {
	font-size: 20px;
	line-height: 1;
	font-weight: 700;
	color: var(--text-primary);
}

.amount span {
	font-weight: 500;
	font-size: 16px;
	color: var(--text-tertiary);
}

.icon {
	width: 44px;
	height: 44px;

	display: flex;
	align-items: center;
	justify-content: center;

	border-radius: 12px;
	border: 1px solid var(--border);
	background: var(--surface-02);
	color: var(--text-secondary);
}

.help_footer {
	margin-top: 12px;
}

@media (max-width: 650px) {
	.wrapper {
		flex-direction: column;

		padding: 20px 0;
	}

	.sector {
		width: 100%;

		padding: 0 20px;
	}

	.sector:nth-child(1),
	.sector:nth-child(2) {
		border-right: initial;
		border-bottom: 1px solid var(--border);
		padding-bottom: 20px;
	}
}
</style>
