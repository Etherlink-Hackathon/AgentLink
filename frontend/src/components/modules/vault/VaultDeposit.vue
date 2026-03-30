<script setup>
import { ref } from "vue"
import Button from "@ui/Button.vue"
import Input from "@ui/Input.vue"

const emit = defineEmits(["onDeposit", "onWithdraw"])

const props = defineProps({
	vault: Object,
})

const activeTab = ref("deposit")
const amount = ref("")

const handlePreset = (preset) => {
	const balance = 14.50 // Mock balance
	if (preset === 'MAX') {
		amount.value = balance.toString()
	} else {
		amount.value = (balance * (preset / 100)).toFixed(2)
	}
}

const handleConfirm = () => {
	if (activeTab.value === 'deposit') {
		emit('onDeposit', amount.value)
	} else {
		emit('onWithdraw', amount.value)
	}
}
</script>

<template>
	<div :class="$style.wrapper">
		<Flex direction="column" gap="24">
			<div :class="$style.switcher">
			<div
				@click="activeTab = 'deposit'"
				:class="[$style.tab, activeTab == 'deposit' && $style.active]"
			>
				Deposit
			</div>
			<div
				@click="activeTab = 'withdraw'"
				:class="[
					$style.tab,
					activeTab == 'withdraw' && $style.active,
				]"
			>
				Withdraw
			</div>
		</div>

			<Flex direction="column" gap="12">
				<Flex justify="between" align="center">
					<Text size="12" weight="700" color="tertiary" :class="$style.label">AMOUNT</Text>
					<Text size="12" weight="700" color="tertiary" :class="$style.balance">Balance: 14.50 {{ vault?.token1?.symbol || 'XTZ' }}</Text>
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

			<Button
					@click="handleConfirm"
					type="primary"
					size="medium"
					keybind="C"
					@onKeybind="handleConfirm"
					block
					style="border-radius: 4px 7px 7px 4px"
				>
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
	background: var(--card-bg);
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
	background: var(--card-bg);
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

.switcher {
	display: flex;

	margin: 0 20px 24px 20px;

	border-radius: 6px;
	box-shadow: 0 0 0 2px var(--border);
}

.tab {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;

	width: 100%;
	height: 28px;
	cursor: pointer;

	font-size: 13px;
	line-height: 1;
	font-weight: 600;
	color: var(--text-primary);

	opacity: 0.7;

	transition: all 0.2s ease;
}

.tab div {
	width: 6px;
	height: 6px;
	border-radius: 50%;
	background: var(--blue);
}

.tab:nth-child(1) {
	border-radius: 6px 0 0 6px;
}

.tab:nth-child(2) {
	border-radius: 0 6px 6px 0;
}

.tab.active {
	background: var(--opacity-05);
	opacity: 1;
}

.tab:active {
	transform: translateY(1px);
}
</style>
