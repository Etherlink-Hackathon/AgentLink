<script setup>
import { ref, computed } from "vue"
import VueApexCharts from "vue3-apexcharts"

const props = defineProps({
	vault: Object,
})

const activePeriod = ref("1W")

const chartOptions = computed(() => ({
	chart: {
		type: 'line',
		toolbar: { show: false },
		background: 'transparent',
		sparkline: { enabled: false },
	},
	stroke: {
		curve: 'smooth',
		width: 3,
		colors: ['#ee5b46']
	},
	theme: { mode: 'dark' },
	fill: {
		type: 'gradient',
		gradient: {
			shadeIntensity: 1,
			opacityFrom: 0.7,
			opacityTo: 0.3,
			stops: [0, 90, 100]
		}
	},
	xaxis: {
		categories: activePeriod.value === '1D' 
			? ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] 
			: activePeriod.value === '1W'
			? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
			: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
		axisBorder: { show: false },
		axisTicks: { show: false },
		labels: {
			style: {
				colors: 'var(--text-tertiary)',
				fontSize: '11px',
				fontWeight: 600,
			}
		}
	},
	yaxis: {
		show: true,
		labels: {
			style: {
				colors: 'var(--text-tertiary)',
				fontSize: '11px',
				fontWeight: 600,
			},
			formatter: (val) => `${val.toFixed(2)}`
		}
	},
	grid: {
		borderColor: 'rgba(255,255,255,0.05)',
		strokeDashArray: 4,
	},
	tooltip: {
		theme: 'dark',
		x: { show: false },
		y: {
			formatter: (val) => `${val} ${props.vault?.token1?.symbol || 'ETH'}`
		}
	}
}))

const series = computed(() => {
	const data = {
		'1D': [0.05, 0.08, 0.07, 0.12, 0.10, 0.15],
		'1W': [0.42, 0.48, 0.52, 0.45, 0.61, 0.58, 0.65],
		'1M': [1.2, 1.8, 1.5, 2.1]
	}
	return [{
		name: 'Earnings',
		data: data[activePeriod.value]
	}]
})
</script>

<template>
	<div :class="$style.wrapper">
		<Flex justify="between" align="center" :class="$style.header">
			<Flex direction="column" gap="4">
				<Text size="14" weight="600" color="primary">Your Earnings</Text>
				<Text size="12" weight="500" color="tertiary">Historical yield performance</Text>
			</Flex>
			
			<div :class="$style.toggles">
				<div 
					v-for="p in ['1D', '1W', '1M']" 
					:key="p"
					@click="activePeriod = p"
					:class="[$style.toggle, activePeriod === p && $style.active]"
				>
					{{ p }}
				</div>
			</div>
		</Flex>

		<div :class="$style.chart_container">
			<VueApexCharts
				type="line"
				height="240"
				width="100%"
				:options="chartOptions"
				:series="series"
			/>
		</div>
	</div>
</template>

<style module>
.wrapper {
	padding: 24px;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
}

.header {
	margin-bottom: 24px;
}

.toggles {
	display: flex;
	gap: 4px;
	background: var(--surface-02);
	padding: 4px;
	border-radius: 6px;
}

.toggle {
	padding: 4px 10px;
	font-size: 12px;
	font-weight: 700;
	color: var(--text-tertiary);
	border-radius: 4px;
	cursor: pointer;
	transition: all 0.2s ease;
}

.toggle:hover {
	color: var(--text-secondary);
}

.toggle.active {
	background: var(--card-bg);
	color: var(--text-primary);
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.chart_container {
	margin: 0 -10px;
}
</style>
