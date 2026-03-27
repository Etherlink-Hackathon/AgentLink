<script setup>
import { ref, reactive, computed, watch } from "vue"

/**
 * UI
 */
import Button from "@ui/Button.vue"
import Toggle from "@ui/Toggle.vue"

/**
 * Services
 */
import { getCurrencyIcon } from "@utils/misc"
import { useAccountStore } from "@store/account"
import { analytics } from "@sdk"

const props = defineProps({
	filters: { type: Object },
	vaults: { type: Array },
	filteredCount: { type: Number },
})

const emit = defineEmits(["onSelect", "onReset", "onUpdateAdvanced"])

const accountStore = useAccountStore()
const selectedTab = ref("Basic")

/** Range Picker State */
const range = reactive({
	min: 0,
	max: 100000,
})

const position = reactive({
	left: 0,
	right: 0,
})

const minInputEl = ref(null)
const maxInputEl = ref(null)

const advancedFiltersCount = computed(() => {
	let count = 0
	if (props.filters.advanced.period) count += 1
	if (props.filters.advanced.participants.length) count += 1
  if (props.filters.strategies.some(s => s.active)) count += 1
	return count
})

const handleReset = () => {
	analytics.log("onResetFilters")
	range.min = 0
	range.max = 100000
	emit("onReset")
}

const handleSelect = (category, item) => {
	emit("onSelect", category, item)
}

/** Range Selection logic */
watch(
	() => range.min,
	(val) => {
		const left = (val * 100) / 100000
		position.left = left > 0 ? left : 0
    emit("onUpdateAdvanced", { liquidity: { ...range } })
	},
)

watch(
	() => range.max,
	(val) => {
		const right = ((100000 - val) * 100) / 100000
		position.right = right > 0 ? right : 0
    emit("onUpdateAdvanced", { liquidity: { ...range } })
	},
)

const handleBlur = (target) => {
	if (target === "min") {
		if (range.min < 0) range.min = 0
	}
	if (target === "max") {
		if (range.max > 100000) range.max = 100000
	}
	if (range.min > range.max) range.min = range.max
}

const handleKeydown = (e) => {
	if (e.key === "-" || e.key === "e") e.preventDefault()
}

/** Participants Management */
const manageParticipant = (address, action) => {
  const participants = [...props.filters.advanced.participants]
  if (action === 'add' && !participants.includes(address)) {
    participants.push(address)
  } else if (action === 'remove') {
    const index = participants.indexOf(address)
    if (index > -1) participants.splice(index, 1)
  }
  emit("onUpdateAdvanced", { participants })
}

</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.title">Filters</div>

		<div :class="$style.switcher">
			<div
				@click="selectedTab = 'Basic'"
				:class="[$style.tab, selectedTab == 'Basic' && $style.active]"
			>
				Basic
			</div>
			<div
				@click="selectedTab = 'Advanced'"
				:class="[$style.tab, selectedTab == 'Advanced' && $style.active]"
			>
				Advanced
				<div v-if="advancedFiltersCount" :class="$style.dot" />
			</div>
		</div>

		<template v-if="selectedTab == 'Basic'">
			<div :class="$style.block">
				<div :class="$style.subtitle">Symbol</div>
				<div :class="$style.badges">
					<div
						v-for="symbol in filters.symbols"
						:key="symbol.name"
						@click="handleSelect('symbols', symbol)"
						:class="[$style.badge, symbol.active && $style.active]"
					>
						<img :src="getCurrencyIcon(symbol.name)" alt="symbol" />
						{{ symbol.name }}
					</div>
				</div>
			</div>

			<div :class="$style.block">
				<div :class="$style.subtitle">Status</div>
				<div :class="$style.badges">
					<div
						v-for="status in filters.statuses"
						:key="status.name"
						@click="handleSelect('statuses', status)"
						:class="[$style.badge, status.active && $style.active, $style[status.color]]"
					>
						<Icon :name="status.icon" size="14" />
						{{ status.name }}
					</div>
				</div>
			</div>

			<div :class="$style.block">
				<div :class="$style.subtitle">Strategies</div>
				<div :class="$style.badges">
					<div
						v-for="strategy in filters.strategies"
						:key="strategy.name"
						@click="handleSelect('strategies', strategy)"
						:class="[$style.badge, strategy.active && $style.active]"
					>
						{{ strategy.name }}
					</div>
				</div>
			</div>
		</template>

		<template v-else>
			<div :class="$style.block">
				<div :class="$style.subtitle">Liquidity Filter (ETH)</div>
				<div :class="$style.range_picker">
					<div :class="$style.range">
						<div
							:class="$style.filled_range"
							:style="{
								left: `${position.left}%`,
								right: `${position.right}%`,
							}"
						/>
					</div>

					<div :class="$style.range_inputs">
						<div @click="minInputEl.focus()" :class="$style.range_input">
							<Icon name="download" size="12" />
							<input
								ref="minInputEl"
								v-model="range.min"
								type="number"
								step="1"
								@keydown="handleKeydown"
								@blur="handleBlur('min')"
								placeholder="0"
							/>
						</div>
						<div @click="maxInputEl.focus()" :class="$style.range_input">
							<input
								ref="maxInputEl"
								v-model="range.max"
								type="number"
								step="1"
								@keydown="handleKeydown"
								@blur="handleBlur('max')"
								placeholder="100k"
                :class="$style.right"
							/>
							<Icon name="download" size="12" :class="$style.reverse" />
						</div>
					</div>
				</div>
			</div>

			<div :class="$style.block">
				<div :class="$style.subtitle">Track Participants</div>
				<div :class="$style.badges">
					<div
						v-if="accountStore.isLoggined"
						@click="manageParticipant(accountStore.pkh, 'add')"
						:class="[$style.badge, $style.active]"
					>
						<img
							:src="`https://services.tzkt.io/v1/avatars/${accountStore.pkh}`"
							:class="$style.avatar"
							alt="avatar"
						/>
						Include Me
					</div>
          <div
						v-for="participant in filters.advanced.participants"
						:key="participant"
						@click="manageParticipant(participant, 'remove')"
						:class="[$style.badge, $style.active]"
					>
						<img
							:src="`https://services.tzkt.io/v1/avatars/${participant}`"
							:class="$style.avatar"
							alt="avatar"
						/>
						{{ participant.slice(0, 6) }}..
					</div>
				</div>
			</div>

			<div :class="$style.block">
				<div :class="$style.subtitle">Creation Period</div>
				<div :class="$style.period">
					<input
						v-model="filters.advanced.period"
						type="date"
						:class="$style.date_input"
					/>
				</div>
			</div>

      <div :class="$style.block">
				<div :class="$style.subtitle">DEX Protocols</div>
				<div :class="$style.badges">
					<div
						v-for="dex in filters.dexs"
						:key="dex.name"
						@click="handleSelect('dexs', dex)"
						:class="[$style.badge, dex.active && $style.active]"
					>
						{{ dex.name }}
					</div>
				</div>
			</div>
		</template>

		<div :class="$style.divider" />

		<div :class="$style.actions">
			<Button @click="handleReset" type="secondary" size="small" block>Reset Filters</Button>

			<div :class="$style.counters">
				<div :class="$style.counter">
					<div :class="$style.counter__left">
						<Icon name="collection" size="16" /> Total:
					</div>
					<div :class="$style.counter__value">{{ vaults.length }}</div>
				</div>
				<div :class="$style.counter">
					<div :class="$style.counter__left">
						<Icon name="filter" size="16" /> Filtered:
					</div>
					<div :class="$style.counter__value">{{ filteredCount }}</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style module>
.wrapper {
	position: sticky;
	top: 100px;
	background: var(--card-bg);
	border-radius: 12px;
	border-top: 3px solid var(--border);
	padding: 24px 0 16px 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.title {
	font-size: 15px;
	font-weight: 700;
	color: var(--text-primary);
	padding: 0 20px;
	margin-bottom: 24px;
}

.switcher {
	display: flex;
	margin: 0 20px 24px 20px;
	border-radius: 8px;
	background: var(--btn-secondary-bg);
	padding: 4px;
}

.tab {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
  gap: 8px;
	height: 32px;
	cursor: pointer;
	font-size: 13px;
	font-weight: 600;
	color: var(--text-secondary);
	border-radius: 6px;
	transition: all 0.2s;
  position: relative;
}

.tab.active {
	background: var(--card-bg);
	color: var(--text-primary);
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand);
}

.block {
	display: flex;
	flex-direction: column;
	gap: 12px;
	padding: 0 20px;
	margin-bottom: 32px;
}

.subtitle {
	font-size: 12px;
	font-weight: 700;
	color: var(--text-tertiary);
	text-transform: uppercase;
	letter-spacing: 0.05em;
}

.badges {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}

.badge {
	display: flex;
	align-items: center;
	gap: 8px;
	height: 32px;
	border: 2px solid var(--border);
	padding: 0 12px;
	border-radius: 50px;
	cursor: pointer;
	font-size: 13px;
	font-weight: 600;
	color: var(--text-secondary);
	transition: all 0.2s;
  background: transparent;
}

.badge:hover {
	border-color: var(--border-highlight);
}

.badge.active {
	border-color: var(--brand);
	color: var(--text-primary);
	background: rgba(167, 139, 250, 0.05);
  opacity: 1;
}

.badge img {
	width: 16px;
	height: 16px;
	border-radius: 50%;
}

.avatar {
  border-radius: 50%;
}

/* Range Picker */
.range_picker {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.range {
	position: relative;
	width: 100%;
	height: 4px;
	background: var(--border);
	border-radius: 2px;
}

.filled_range {
	position: absolute;
	height: 100%;
	background: var(--brand);
	border-radius: 2px;
}

.range_inputs {
	display: flex;
	justify-content: space-between;
}

.range_input {
	display: flex;
	align-items: center;
	gap: 6px;
	background: var(--btn-secondary-bg);
	border: 1px solid var(--border);
	border-radius: 6px;
	padding: 4px 8px;
	font-size: 13px;
}

.range_input input {
	width: 50px;
	background: transparent;
	border: none;
	color: var(--text-primary);
	font-weight: 600;
	font-size: 13px;
}

.range_input input.right {
  text-align: right;
}

.reverse {
  transform: rotate(180deg);
}

/* Date Input */
.date_input {
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 600;
  width: 100%;
}

/* Status colors */
.badge.purple.active { border-color: var(--purple); background: rgba(161, 131, 246, 0.1); }
.badge.yellow.active { border-color: var(--yellow); background: rgba(245, 158, 11, 0.1); }
.badge.green.active { border-color: var(--green); background: rgba(16, 185, 129, 0.1); }

.divider {
	height: 1px;
	background: var(--border);
	margin: 20px 20px 24px;
}

.actions {
	padding: 0 20px;
}

.counters {
	display: flex;
	justify-content: space-between;
	margin-top: 20px;
}

.counter {
	display: flex;
	align-items: center;
	gap: 8px;
}

.counter__left {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 12px;
	font-weight: 600;
	color: var(--text-tertiary);
}

.counter__value {
	font-size: 13px;
	font-weight: 700;
	color: var(--text-primary);
}
</style>
