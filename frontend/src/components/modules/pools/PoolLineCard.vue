<script setup>
/**
 * Vendor
 */
import { computed } from "vue"

/**
 * Local
 */
import { EventCardShort } from "@local/EventCard"

/**
 * Services
 */
import { parseDateTime } from "@utils/date"
import { numberWithSymbol } from "@utils/amounts"

const props = defineProps({
	line: {
		type: Object,
		required: true,
	},
})

const progress = computed(() => {
    if (!props.line.maxEvents) return 0
    return (props.line.activeEventsCount / props.line.maxEvents) * 100
})
</script>

<template>
	<Flex direction="column" gap="20" :class="$style.card">
		<Flex justify="between" align="center">
			<Flex align="center" gap="12">
				<Icon :name="line.currencyPair.symbol.split('-')[0].toLowerCase()" size="24" />
				<Flex direction="column" gap="4">
					<Text size="14" weight="600" color="primary">
						{{ line.currencyPair.symbol }} Line
					</Text>
					<Text size="12" weight="500" color="tertiary">
						Template #{{ line.id }}
					</Text>
				</Flex>
			</Flex>

			<div :class="[$style.status, line.isPaused && $style.paused]">
				<Text size="11" weight="700" color="white" transform="uppercase">
					{{ line.isPaused ? 'Paused' : 'Active' }}
				</Text>
			</div>
		</Flex>

		<Flex direction="column" gap="12">
			<Flex justify="between">
				<Text size="12" weight="600" color="tertiary"> Target Dynamics </Text>
				<Text size="12" weight="600" color="primary"> {{ line.targetDynamics / 100 }}% </Text>
			</Flex>
			<Flex justify="between">
				<Text size="12" weight="600" color="tertiary"> Liquidity Backing </Text>
				<Text size="12" weight="600" color="primary"> {{ line.liquidityPercent / 100 }}% </Text>
			</Flex>
			<Flex justify="between">
				<Text size="12" weight="600" color="tertiary"> Measure Period </Text>
				<Text size="12" weight="600" color="primary"> {{ line.measurePeriod / 3600 }}h </Text>
			</Flex>
		</Flex>

		<div :class="$style.divider" />

		<Flex direction="column" gap="8">
			<Flex justify="between">
				<Text size="12" weight="600" color="tertiary"> Capacity </Text>
				<Text size="12" weight="600" color="primary"> 
                    {{ line.activeEventsCount }} / {{ line.maxEvents }} Events 
                </Text>
			</Flex>
			<div :class="$style.progress">
				<div :class="$style.progress__bar" :style="{ width: `${progress}%` }" />
			</div>
		</Flex>

		<Flex justify="between" align="center">
			<Text size="12" weight="600" color="tertiary"> Last event created </Text>
			<Text size="12" weight="600" color="primary">
				{{ parseDateTime(line.lastBetsCloseTime, "MMM D, HH:mm") }}
			</Text>
		</Flex>
	</Flex>
</template>

<style module>
.card {
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
	padding: 20px;
    transition: all 0.2s ease;
}

.card:hover {
    border-color: var(--brand);
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.status {
	background: var(--green);
	padding: 4px 8px;
	border-radius: 6px;
    box-shadow: 0 4px 8px rgba(26, 161, 104, 0.2);
}

.status.paused {
	background: var(--tertiary);
    box-shadow: none;
}

.divider {
	height: 1px;
	background: var(--border);
}

.progress {
	height: 6px;
	background: rgba(255, 255, 255, 0.05);
	border-radius: 100px;
	overflow: hidden;
}

.progress__bar {
	height: 100%;
	background: linear-gradient(90deg, var(--brand), #8b5cf6);
	border-radius: 100px;
    transition: width 1s ease-in-out;
}
</style>
