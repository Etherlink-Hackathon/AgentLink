<script setup>
import { ref } from "vue"
import Button from "@ui/Button.vue"
import Input from "@ui/Input.vue"

const props = defineProps({
	vault: Object,
})

const activeTab = ref("deposit")
const amount = ref("")

const handlePreset = (preset) => {
	if (preset === 'MAX') {
		amount.value = "14.50"
	} else {
		amount.value = (14.50 * (preset / 100)).toFixed(2)
	}
}
</script>

<template>
	<div :class="$style.wrapper">
		<Flex direction="column" gap="24">
			<div :class="$style.tabs">
				<div
					@click="activeTab = 'deposit'"
					:class="[$style.tab, activeTab === 'deposit' && $style.active]"
				>
					Deposit
				</div>
				<div
					@click="activeTab = 'withdraw'"
					:class="[$style.tab, activeTab === 'withdraw' && $style.active]"
				>
					Withdraw
				</div>
			</div>

			<Flex direction="column" gap="12">
				<Flex justify="between" align="center">
					<Text size="12" weight="700" color="tertiary" :class="$style.label">AMOUNT</Text>
					<Text size="12" weight="700" color="tertiary" :class="$style.balance">Balance: 14.50 {{ vault?.token1?.symbol || 'WETH' }}</Text>
				</Flex>
				<Input
					v-model="amount"
					placeholder="0.0"
					type="number"
					:class="$style.input_field"
				>
					<template #right>
						<Text size="14" weight="700" color="secondary">{{ vault?.token1?.symbol || 'WETH' }}</Text>
					</template>
				</Input>

				<Flex gap="8" :class="$style.amount_presets">
					<div 
						v-for="preset in [25, 50, 75, 'MAX']" 
						:key="preset"
						@click="handlePreset(preset)"
						:class="$style.preset_btn"
					>
						{{ preset }}{{ preset === 'MAX' ? '' : '%' }}
					</div>
				</Flex>
			</Flex>

			<Flex direction="column" gap="16" :class="$style.info">
				<Flex justify="between" align="center">
					<Text size="13" weight="600" color="tertiary">Estimated Monthly Yield</Text>
					<Text size="13" weight="700" color="green">+$120.50</Text>
				</Flex>
				<Flex justify="between" align="center">
					<Text size="13" weight="600" color="tertiary">Protocol Fee (0.1%)</Text>
					<Text size="13" weight="700" color="secondary">0.00 {{ vault?.token1?.symbol || 'WETH' }}</Text>
				</Flex>
			</Flex>

			<Button type="white" size="large" block :class="$style.confirm_btn">
				{{ activeTab === 'deposit' ? 'Confirm Deposit' : 'Confirm Withdrawal' }}
			</Button>

			<div :class="$style.disclaimer_container">
        <Icon name="help" size="14" :class="$style.help_icon" />
        <Text size="12" weight="500" color="support" :class="$style.disclaimer">
          Funds are deployed into automated strategies. Withdrawal processing may take up to 24 hours depending on strategy liquidity.
        </Text>
      </div>
		</Flex>
	</div>
</template>

<style module>
.wrapper {
	padding: 28px;
	background: var(--surface-01);
	border: 1px solid var(--border);
	border-radius: 12px;
	height: fit-content;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.tabs {
	display: flex;
	background: var(--surface-02);
	padding: 4px;
	border-radius: 10px;
}

.tab {
	flex: 1;
	text-align: center;
	padding: 10px;
	font-size: 14px;
	font-weight: 700;
	color: var(--text-tertiary);
	border-radius: 8px;
	cursor: pointer;
	transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab:hover {
  color: var(--text-secondary);
}

.tab.active {
	background: var(--surface-01);
	color: var(--text-primary);
	box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.label {
  letter-spacing: 0.05em;
}

.max {
	cursor: pointer;
  transition: opacity 0.2s;
}

.max:hover {
  opacity: 0.8;
}

.input_field {
  background: var(--surface-02);
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.input_field:focus-within {
  border-color: var(--brand);
}

.info {
	padding: 16px;
	background: var(--surface-02);
	border-radius: 10px;
}

.confirm_btn {
	height: 48px;
	font-size: 15px;
	font-weight: 700;
	box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
}

.amount_presets {
	display: flex;
}

.preset_btn {
	flex: 1;
	text-align: center;
	padding: 8px 0;
	background: var(--surface-02);
	border-radius: 6px;
	font-size: 12px;
	font-weight: 700;
	color: var(--text-tertiary);
	cursor: pointer;
	transition: all 0.2s;
}

.preset_btn:hover {
	background: var(--surface-03);
	color: var(--text-secondary);
}

.balance {
	opacity: 0.8;
}

.disclaimer_container {
  display: flex;
  gap: 10px;
  background: rgba(167, 139, 250, 0.05);
  padding: 12px;
  border-radius: 8px;
}

.help_icon {
  fill: var(--text-tertiary);
  flex-shrink: 0;
  margin-top: 2px;
}

.disclaimer {
	line-height: 1.5;
  color: var(--text-tertiary);
}
</style>
