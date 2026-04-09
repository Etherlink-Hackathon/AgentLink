<script setup>
/**
 * Vendor
 */
import { computed } from "vue"

/**
 * Utils
 */
import { abbreviateNumber } from "@utils/amounts"
import { currentNetwork } from "@sdk"
import { chainConfig } from "@config"

const props = defineProps({
	vault: Object,
})

const tvl = computed(() => {
	const val = parseFloat(props.vault?.tvl || 0)
	// if (val >= 1e6) return abbreviateNumber(val)
	// return val.toLocaleString(undefined, { 
	// 	minimumFractionDigits: 2,
	// 	maximumFractionDigits: 2 
	// })
	return val;
})

const revenue = computed(() => {
	const val = parseFloat(props.vault?.revenue || 0)
	if (val >= 1e6) return abbreviateNumber(val)
	return val.toLocaleString(undefined, { 
		minimumFractionDigits: 2,
		maximumFractionDigits: 6 
	})
})

const apy = computed(() => {
	const val = parseFloat(props.vault?.apy || 0)
	return val.toLocaleString(undefined, { 
		minimumFractionDigits: 0,
		maximumFractionDigits: 2 
	})
})

const activeStrategies = computed(() => {
	return props.vault?.vaultsPools?.length || 0
})
</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">TOTAL VALUE LOCKED</Text>
			<Text size="24" weight="700" color="primary">{{ tvl }} {{ chainConfig[currentNetwork.value]?.nativeCurrency?.symbol || 'ꜩ' }}</Text>
		</div>
		<div :class="$style.divider" />
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">AVERAGE APY</Text>
			<Text size="24" weight="700" color="green">{{ apy }}%</Text>
		</div>
		<div :class="$style.divider" />
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">24H YIELD REVENUE</Text>
			<Text size="24" weight="700" color="primary">{{ revenue }} {{ chainConfig[currentNetwork.value]?.nativeCurrency?.symbol || 'ꜩ' }}</Text>
		</div>
		<div :class="$style.divider" />
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">ACTIVE DEX POOLS</Text>
			<Text size="24" weight="700" color="primary">{{ activeStrategies }}</Text>
		</div>
	</div>
</template>

<style module>
.wrapper {
	display: flex;
	align-items: center;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
	padding: 24px;
	gap: 40px;
}

.stat {
	display: flex;
	flex-direction: column;
	gap: 8px;
	flex: 1;
}

.label {
	letter-spacing: 0.05em;
}

.divider {
	width: 1px;
	height: 40px;
	background: var(--border);
}

@media (max-width: 900px) {
	.wrapper {
		background: var(--card-bg);
		flex-direction: column;
		align-items: flex-start;
		gap: 24px;
	}

	.divider {
		width: 100%;
		height: 1px;
	}
}
</style>
