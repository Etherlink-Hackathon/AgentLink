<script setup>
const props = defineProps({
	vault: Object,
})
</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">TOTAL VALUE LOCKED</Text>
			<Text size="24" weight="700" color="primary">${{ (vault?.tvl || 0).toLocaleString() }}</Text>
		</div>
		<div :class="$style.divider" />
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">AVERAGE APY</Text>
			<Text size="24" weight="700" color="green">{{ vault?.apy || 0 }}%</Text>
		</div>
		<div :class="$style.divider" />
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">24H YIELD REVENUE</Text>
			<Text size="24" weight="700" color="primary">${{ ((vault?.tvl || 0) * 0.0005).toLocaleString() }}</Text>
		</div>
		<div :class="$style.divider" />
		<div :class="$style.stat">
			<Text size="12" weight="600" color="tertiary" :class="$style.label">ACTIVE STRATEGIES</Text>
			<Text size="24" weight="700" color="primary">4</Text>
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
