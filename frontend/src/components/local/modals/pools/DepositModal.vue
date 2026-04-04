<script setup>
/**
 * Vendor
 */
import { ref, reactive, watch, computed, nextTick } from "vue"
import { DateTime } from "luxon"
import { ethers } from "ethers"
import BN from "bignumber.js"

/**
 * UI
 */
import LoadingBar from "@ui/LoadingBar.vue"
import Modal from "@ui/Modal.vue"
import Input from "@ui/Input.vue"
import Button from "@ui/Button.vue"
import Tooltip from "@ui/Tooltip.vue"
import LoadingDots from "@ui/LoadingDots.vue"

/**
 * Services
 */
import { 
	flameWager as juster, 
	analytics, 
	getAllowance, 
	approve 
} from "@sdk"
import { shorten } from "@utils/misc"
import { sanitizeInput, capitalizeFirstLetter, parsePoolName } from "@utils/misc"
import { numberWithSymbol } from "@utils/amounts"

/**
 * Store
 */
import { useAccountStore } from "@store/account"
import { useNotificationsStore } from "@store/notifications"

/**
 * Config
 */
import { activeChainConfig } from "@config"

const accountStore = useAccountStore()
const notificationsStore = useNotificationsStore()

const props = defineProps({
	show: Boolean,
	selectedPool: Object,
	state: Object,
	apy: Number,
	initialAmount: [Number, String],
})

const emit = defineEmits(["onClose", "onBack"])

const inputEl = ref(null)
const amount = reactive({ value: 0, error: "" })
const allowance = ref(0n)
const approveTxHash = ref("")
const depositTxHash = ref("")

const progressStatus = computed(() => {
	if (depositTxHash.value) return "Completed"
	if (opConfirmationInProgress.value || isApproving.value) return "Processing"
	return "Not Started"
})

const balanceToAmountRatio = computed(() => {
	const balance = accountStore.balance || 0
	const percent = balance > 0 ? (amount.value * 100) / balance : 0

	let status = "awaiting"
	if (percent > 0 && percent < 40) status = "ok"
	else if (percent >= 40 && percent < 70) status = "medium"
	else if (percent >= 70) status = "bad"

	return {
		percent,
		status,
	}
})

const depositInShares = computed(() => amount.value / props.state.sharePrice)

const opConfirmationInProgress = ref(false)
const isApproving = ref(false)

const fetchAllowance = async () => {
	if (!accountStore.pkh || !props.selectedPool?.address) return
	try {
		const res = await getAllowance(props.selectedPool.address, accountStore.pkh)
		allowance.value = res
	} catch (err) {
		console.error("Failed to fetch allowance:", err)
	}
}

const handleDeposit = async () => {
	if (buttonState.value.disabled) return

	try {
		const vaultAddress = props.selectedPool.address
		const assets = ethers.parseUnits((amount.value || 0).toString(), 18)

		// 1. Approve Token
		if (allowance.value < assets) {
			isApproving.value = true
			const tx = await approve(vaultAddress, assets)
			approveTxHash.value = tx.hash
			
			notificationsStore.create({
				notification: {
					type: "info",
					title: "Approval started",
					description: "Please confirm the approval in your wallet",
					autoDestroy: true,
				},
			})

			await tx.wait()
			await fetchAllowance()
			isApproving.value = false
			
			notificationsStore.create({
				notification: {
					type: "success",
					title: "Approval successful",
					description: "Now you can proceed with the deposit",
					autoDestroy: true,
				},
			})
			return
		}

		// 2. Deposit
		opConfirmationInProgress.value = true
		const op = await juster.vaults[vaultAddress.toLowerCase()].deposit(assets, accountStore.pkh)
		depositTxHash.value = op.hash

		accountStore.pendingTransaction.awaiting = true
		op.wait()
			.then(() => {
				accountStore.pendingTransaction.awaiting = false
			})
			.catch(() => {
				accountStore.pendingTransaction.awaiting = false
			})

		notificationsStore.create({
			notification: {
				type: "success",
				title: "Your deposit has been accepted",
				description: "We need to process your deposit, it will take ~30 seconds",
				autoDestroy: true,
			},
		})

		analytics.log("onPoolDeposit", {
			pool: props.selectedPool.address,
			amount: amount.value,
		})

		opConfirmationInProgress.value = false
		emit("onClose")
	} catch (error) {
		console.log(error)

		if (error.title == "Aborted") {
			notificationsStore.create({
				notification: {
					icon: "warning",
					title: "The operation was rejected",
					description: `The deposit to ${props.selectedPool.name} of ${amount.value} TIA was not accepted`,
					autoDestroy: true,
				},
			})
		} else {
			notificationsStore.create({
				notification: {
					icon: "warning",
					title: "Something went wrong",
					description: "Repeat the operation or wait for a while",
					autoDestroy: true,
				},
			})
		}

		opConfirmationInProgress.value = false
	}
}

const buttonState = computed(() => {
	if (accountStore.pendingTransaction.awaiting)
		return {
			text: "Previous transaction in process",
			disabled: true,
		}
	if (opConfirmationInProgress.value) {
		return { text: "Processing Deposit...", disabled: true, type: "primary" }
	}
	if (isApproving.value) {
		return { text: "Approving Assets...", disabled: true, type: "primary" }
	}
	if (!amount.value)
		return {
			text: "Type deposit amount",
			disabled: true,
			type: "secondary",
		}
	if (amount.value > 0 && amount.value < 0.01) return { text: "Minimum 0.01 XTZ", disabled: true, type: "secondary" }
	if (amount.value > accountStore.balance)
		return {
			text: "Insufficient funds",
			disabled: true,
			type: "secondary",
		}

	if (amount.value > 0) {
		const assets = ethers.parseUnits((amount.value || 0).toString(), 18)
		if (allowance.value < assets) {
			return {
				text: "Approve Assets",
				disabled: false,
				type: "primary",
			}
		}
	}

	return {
		text: `Deposit to ${parsePoolName(props.selectedPool.name)}`,
		disabled: false,
		type: "primary",
	}
})

const handleKeydown = (e) => {
	sanitizeInput(e)
}

let timingInterval = null
const timing = reactive({
	create: null,
	accept: null,
})
const initTiming = () => {
	timing.create = DateTime.now().setLocale("en")
	timing.accept = DateTime.now().setLocale("en").plus({
		seconds: props.selectedPool.entryLockPeriod,
	})
}

const getEntryLockPeriodText = () => {
	const diff = DateTime.now()
		.plus({ seconds: props.selectedPool.entryLockPeriod })
		.diff(DateTime.now(), ["days", "hours", "minutes"])
		.toObject()

	if (diff.days && diff.days >= 1) {
		return `${diff.days}d`
	} else if (diff.hours && diff.hours >= 1) {
		return `${diff.hours}h`
	} else if (diff.minutes && diff.minutes >= 1) {
		return `${diff.minutes}m`
	} else {
		return `Instant`
	}
}

watch(
	() => props.show,
	() => {
		if (props.show) {
			if (accountStore.isLoggined) {
				accountStore.updateBalance()
				fetchAllowance()
			}

			amount.value = props.initialAmount || 0
			initTiming()
			timingInterval = setInterval(() => {
				initTiming()
			}, 5_000)

			/** Delay to avoid accidental triggering */
			setTimeout(() => {
				document.addEventListener("keydown", onKeydown)
			}, 500)

			nextTick(() => {
				inputEl.value.$el.querySelector("input").focus()
			})
		} else {
			clearInterval(timingInterval)

			amount.value = 0

			document.removeEventListener("keydown", onKeydown)
		}
	},
)

const onKeydown = (e) => {
	if (e.code == "Enter") {
		e.preventDefault()
		handleDeposit()
	}
}
</script>

<template>
	<Modal new :show="show" width="550" closable @onClose="emit('onClose')">
		<Flex align="center" justify="between" :class="$style.head">
			<Flex align="center" gap="8">
				<Icon name="server" size="16" color="secondary" />

				<Text @click="emit('onBack')" size="14" weight="600" color="secondary" :class="$style.head_btn"> Deposit Liquidity </Text>

				<Icon name="arrow" size="12" color="tertiary" :class="$style.arrow_icon" />

				<Text size="14" weight="600" color="primary">
					{{ parsePoolName(selectedPool.name.replace("Juster Pool: ", "")) }}
				</Text>
			</Flex>

			<Icon @click="emit('onClose')" name="close" size="16" color="tertiary" :class="$style.close_icon" />
		</Flex>

		<Flex direction="column" gap="32" :class="$style.base">
			<Flex direction="column" gap="8">
				<Flex align="center" justify="between" :class="$style.pool">
					<Flex align="center" gap="20">
						<Flex direction="column" gap="8">
							<Text size="14" weight="600" color="primary">
								{{ selectedPool.name.replace("Juster Pool: ", "") }}
							</Text>

							<Flex align="center" gap="8">
								<Flex align="center" gap="4">
									<Icon name="zap_circle" size="12" color="green" />
									<Text size="12" weight="700" color="green">Active</Text>
								</Flex>

								<Text size="8" color="support">✦</Text>

								<Text size="12" weight="600" color="tertiary">Pool</Text>
							</Flex>
						</Flex>
					</Flex>

					<Flex align="center" gap="24">
						<Flex direction="column" gap="8" align="end">
							<Flex align="center" gap="6">
								<Icon name="coins" size="12" color="tertiary" />

								<Text v-if="state" size="14" weight="600" color="primary">
									{{ numberWithSymbol(state.totalLiquidity, ",") }}
								</Text>
								<LoadingDots v-else />

								<template v-if="amount.value > 0">
									<Text size="14" weight="600" color="tertiary">
										+
										{{ numberWithSymbol(amount.value, ",") }}
										=
									</Text>
									<Text size="14" weight="600" color="secondary">
										{{
											numberWithSymbol(
												state.totalLiquidity.toNumber
													? state.totalLiquidity.toNumber() + amount.value
													: state.totalLiquidity + amount.value,
												",",
											)
										}}
									</Text>
								</template>
							</Flex>

							<Text size="12" weight="600" color="tertiary"> Total Value Locked </Text>
						</Flex>

						<Flex direction="column" gap="8" align="end">
							<Flex align="center" gap="6">
								<Icon
									name="stars"
									size="14"
									:color="
										(apy * 100 < 0 && 'red') ||
										(apy * 100 < 40 && 'tertiary') ||
										(apy * 100 < 80 && 'yellow') ||
										(apy * 100 >= 100 && 'green') ||
										'tertiary'
									"
								/>
								<Text size="14" weight="600" color="primary"> {{ numberWithSymbol(apy * 100, ",") }}% </Text>
							</Flex>

							<Text size="12" weight="600" color="tertiary"> APY </Text>
						</Flex>
					</Flex>
				</Flex>
			</Flex>

			<Input
				ref="inputEl"
				type="number"
				:limit="1000000"
				label="Amount"
				placeholder="Deposit amount"
				subtext="ꜩ"
				v-model="amount.value"
				@keydown="handleKeydown"
				:class="$style.amount_input"
			>
				<template v-slot:rightText>
					<Tooltip placement="bottom-end">
						<Flex align="center" gap="4">
							<Icon
								:name="balanceToAmountRatio.status !== 'bad' ? 'checkcircle' : 'warning'"
								size="12"
								:color="
									(balanceToAmountRatio.status === 'awaiting' && 'tertiary') ||
									(balanceToAmountRatio.status === 'ok' && 'green') ||
									(balanceToAmountRatio.status === 'medium' && 'yellow') ||
									(balanceToAmountRatio.status === 'bad' && 'red')
								"
							/>
							<Text size="12" weight="700" color="secondary">
								{{
									balanceToAmountRatio.percent > 0 && balanceToAmountRatio.percent < 1
										? "<1"
										: balanceToAmountRatio.percent.toFixed(0)
								}}%
							</Text>
						</Flex>

						<template #content>
							<Flex direction="column" gap="6" align="end" :class="$style.tooltip_card">
								<Flex>
									<span>Balance status:</span>&nbsp;
									{{ capitalizeFirstLetter(balanceToAmountRatio.status) }}
								</Flex>

								<Flex>
									<span>My funds:</span>&nbsp;
									{{ accountStore.balance }}
								</Flex>

								<Flex>
									<span>Raw Ratio:</span>&nbsp;
									{{ balanceToAmountRatio.percent.toFixed(2) }}
								</Flex>
							</Flex>
						</template>
					</Tooltip>
				</template>
			</Input>
			
						<Flex direction="column" gap="8">
				<Flex align="center" justify="between">
					<Text size="12" weight="600" color="secondary"> Deposit Details </Text>
					<Text size="12" weight="600" color="support"> Approximate calculation </Text>
				</Flex>

				<!-- Deposit to Shares -->
				<Flex align="center" justify="between" :class="$style.badge">
					<Flex align="center" gap="8">
						<Icon name="coins" size="14" color="tertiary" />

						<Flex align="center">
							<Text size="14" weight="600" color="primary">
								{{ amount.value ? numberWithSymbol(amount.value, ",") : 0 }} </Text
							>&nbsp; <Text size="14" weight="600" color="tertiary"> {{activeChainConfig.nativeCurrency.symbol}} </Text>&nbsp;
							<Text size="14" weight="600" color="support"> -> </Text>&nbsp;
							<Text size="14" weight="600" color="secondary"> ~ </Text>
							<Text size="14" weight="600" color="primary">
								{{ amount.value ? numberWithSymbol(depositInShares, ",") : 0 }} </Text
							>&nbsp;
							<Text size="14" weight="600" color="tertiary"> shares </Text>
						</Flex>
					</Flex>

					<Flex align="center" gap="8">
						<Icon name="banknote" size="14" color="tertiary" />
						<Text size="14" weight="600" color="primary">
							{{ state.sharePrice.toFixed(2) }}
						</Text>
					</Flex>
				</Flex>

				<!-- Timing -->
				<!-- <Flex align="center" justify="between" :class="$style.badge">
					<Flex align="center" gap="8">
						<Icon name="plus_circle" size="14" color="tertiary" />

						<Flex align="center">
							<Text size="14" weight="600" color="primary">
								{{ capitalizeFirstLetter(timing.create.toRelativeCalendar()) }}
							</Text>
							&nbsp;
							<Text size="14" weight="600" color="tertiary"> at </Text>
							&nbsp;
							<Text size="14" weight="600" color="primary">
								{{ timing.create.toFormat("HH:mm") }}
							</Text>
						</Flex>
					</Flex>

					<div v-for="i in 5" :class="$style.dot" />
					<Text size="14" weight="600" color="tertiary"> {{ getEntryLockPeriodText() }}</Text>
					<div v-for="i in 5" :class="$style.dot" />

					<Flex align="center" gap="8">
						<Icon name="checkcircle" size="14" color="tertiary" />

						<Flex align="center">
							<Text size="14" weight="600" color="primary">
								{{ capitalizeFirstLetter(timing.accept.toRelativeCalendar()) }}
							</Text>
							&nbsp;
							<Text size="14" weight="600" color="tertiary">at</Text>&nbsp;
							<Text size="14" weight="600" color="primary">
								{{ timing.accept.toFormat("HH:mm") }}
							</Text>
						</Flex>
					</Flex>
				</Flex> -->
			</Flex>

			<!-- Transaction Progress -->
			<Flex direction="column" :class="$style.progress_container">
				<Flex align="center" justify="between">
					<Text size="12" weight="600" color="secondary">Transaction Progress</Text>
					<Flex align="center" gap="4">
						<LoadingDots v-if="progressStatus === 'Processing'" size="12" />
						<Text size="12" weight="600" color="support">
							{{ progressStatus }}
						</Text>
					</Flex>
				</Flex>

				<Flex direction="column" gap="16" :class="$style.progress_steps">
					<!-- Step 1 -->
					<Flex align="center" gap="12">
						<div :class="[$style.circle, allowance >= ethers.parseUnits((amount.value || 0).toString(), 18) ? $style.completed : isApproving ? $style.active : '']">
							<Icon v-if="allowance >= ethers.parseUnits((amount.value || 0).toString(), 18)" name="check" size="10" color="white" />
							<span v-else>1</span>
						</div>
						<Flex direction="column" gap="4">
							<Text size="14" weight="600" :color="allowance >= ethers.parseUnits((amount.value || 0).toString(), 18) ? 'primary' : 'secondary'">Approve Token</Text>
							<a v-if="approveTxHash" :href="`${activeChainConfig.blockExplorerUrls[0]}/tx/${approveTxHash}`" target="_blank" :class="$style.tx_link">
								{{ shorten(approveTxHash) }}
								<Icon name="arrow-up-right" size="10" />
							</a>
						</Flex>
					</Flex>

					<div :class="$style.dashed_line" />

					<!-- Step 2 -->
					<Flex align="center" gap="12">
						<div :class="[$style.circle, depositTxHash ? $style.completed : opConfirmationInProgress ? $style.active : '']">
							<Icon v-if="depositTxHash" name="check" size="10" color="white" />
							<span v-else>2</span>
						</div>
						<Flex direction="column" gap="4">
							<Text size="14" weight="600" :color="depositTxHash ? 'primary' : 'secondary'">Deposit</Text>
							<a v-if="depositTxHash" :href="`${activeChainConfig.blockExplorerUrls[0]}/tx/${depositTxHash}`" target="_blank" :class="$style.tx_link">
								{{ shorten(depositTxHash) }}
								<Icon name="arrow-up-right" size="10" />
							</a>
						</Flex>
					</Flex>
				</Flex>
			</Flex>


			<Flex direction="column" gap="12" align="center">
				<Button
					@click="handleDeposit"
					:type="buttonState.type"
					:disabled="buttonState.disabled"
					:loading="opConfirmationInProgress"
					size="large"
					block
				>
					<LoadingBar v-if="opConfirmationInProgress" size="16" />
					<template v-else>
						<Icon name="plus_circle" size="16" color="white" />
						{{ buttonState.text }}
					</template>
				</Button>

			</Flex>
		</Flex>
	</Modal>
</template>

<style module>
.head {
	height: 56px;

	padding: 0 20px;
}

.head_btn {
	cursor: pointer;
}

.close_icon {
	cursor: pointer;
}

.base {
	padding: 8px 20px 20px 20px;
}

.pool {
	height: 66px;

	background: rgba(255, 255, 255, 0.05);
	border-radius: 8px;

	padding: 0 16px;
}

.arrow_icon {
	transform: rotate(-90deg);
}

.badge {
	height: 38px;

	border-radius: 8px;
	background: rgba(255, 255, 255, 0.05);

	padding: 0 12px;
}

.dot {
	width: 4px;
	height: 4px;
	border-radius: 50%;
	background: var(--text-support);
}

.progress_container {
	overflow: hidden;
}

.progress_steps {
	padding: 20px 16px;
	position: relative;
}

.circle {
	width: 24px;
	height: 24px;
	border-radius: 50%;
	border: 1.5px dashed rgba(255, 255, 255, 0.15);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 11px;
	font-weight: 700;
	color: var(--text-tertiary);
	z-index: 2;
	background: var(--app-bg);
}

.circle.active {
	border: 1.5px solid var(--blue);
	color: var(--blue);
	box-shadow: 0 0 8px rgba(43, 107, 243, 0.3);
}

.circle.completed {
	border: 1.5px solid var(--green);
	background: var(--green);
	color: white;
}

.dashed_line {
	position: absolute;
	top: 44px;
	left: 27.5px;
	bottom: 44px;
	width: 1px;
	border-left: 1.5px dashed rgba(255, 255, 255, 0.1);
	z-index: 1;
}

.tx_link {
	font-size: 11px;
	font-weight: 600;
	color: var(--blue);
	text-decoration: none;
	display: flex;
	align-items: center;
	gap: 4px;
	opacity: 0.8;
	transition: opacity 0.2s;
}

.tx_link:hover {
	opacity: 1;
}
</style>
