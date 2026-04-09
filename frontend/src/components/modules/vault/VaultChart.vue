<script setup>
import { ref } from "vue"
import VueApexCharts from "vue3-apexcharts"

const props = defineProps({
	vault: Object,
})

const activePeriod = ref("1D")

const chartOptions = {
	chart: {
		type: 'bar',
		toolbar: { show: false },
		background: 'transparent',
	},
	theme: { mode: 'dark' },
	colors: ['#276ef1'],
	plotOptions: {
		bar: {
			borderRadius: 4,
			columnWidth: '60%',
		}
	},
	dataLabels: { enabled: false },
	xaxis: {
		categories: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
		axisBorder: { show: false },
		axisTicks: { show: false },
	},
	yaxis: { show: false },
	grid: {
		borderColor: 'rgba(255,255,255,0.05)',
		strokeDashArray: 4,
	},
	tooltip: {
		theme: 'dark',
		y: {
			formatter: (val) => `${val} XTZ`
		}
	}
}

const series = ref([
	{
		name: 'Yield Revenue',
		data: [0.02, 0.03, 0.05, 0.07, 0.13, 0.2]
	}
])
</script>

<template>
	<div :class="$style.wrapper">
		<Flex justify="between" align="center" :class="$style.header">
			<Text size="14" weight="600" color="primary">Yield Revenue</Text>
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

		<VueApexCharts
			type="bar"
			height="240"
			width="100%"
			:options="chartOptions"
			:series="series"
		/>
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
	font-weight: 600;
	color: var(--text-tertiary);
	border-radius: 4px;
	cursor: pointer;
	transition: all 0.2s ease;
}

.toggle.active {
	background: var(--card-bg);
	color: var(--text-primary);
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
