<script setup>
/**
 * Vendor
 */
import { ref, computed } from "vue"
import { DateTime } from "luxon"
import cloneDeep from "lodash.clonedeep"

/**
 * UI
 */
import LoadingBar from "@ui/LoadingBar.vue"
import Modal from "@ui/Modal.vue"
import Button from "@ui/Button.vue"
import Pagination from "@ui/Pagination.vue"

/**
 * Services
 */
import { redeem, flameWager } from "@sdk"
import { shorten } from "@utils/misc"
import { numberWithSymbol } from "@utils/amounts"

/**
 * Store
 */
import { useAccountStore } from "@store/account"
import { useNotificationsStore } from "@store/notifications"

const accountStore = useAccountStore()
const notificationsStore = useNotificationsStore()

const props = defineProps({
	show: Boolean,
	vault: Object,
	position: Object, // { netPosition, redeemableAssets, onChainShares, totalRewardsEarned }
})

const emit = defineEmits(["onClose"])

/** Simulating legacy "Claims" structure for UI consistency */
const pendingClaims = ref([]) // Etherlink vaults have instant claims usually
const availableClaims = computed(() => {
	if (!props.position || !props.position.redeemableAssets || props.position.redeemableAssets === "0") return []
	console.log(props.position)
	// Map vault position to a single claim structure that the UI expects
	return {
		id: props.vault?.address?.slice(-4) || 'Vault',
		amount: parseFloat(props.position.redeemableAssets) / 10**18,
		poolId: props.vault?.address || '0x0',
		eventId: '0',
		withdrawn: false
	}
})

const nextClaim = computed(() => null)

const opConfirmationInProgress = ref(false)

const handleWithdraw = async () => {
	if (buttonState.disabled || !props.vault || !props.position) return

	const address = accountStore.pkh || flameWager.address
	if (!address) return

	const shares = props.position.onChainShares
	if (!shares || shares === "0") return

	try {
		opConfirmationInProgress.value = true
		
		const tx = await redeem(props.vault.address, BigInt(shares), address)
		
		notificationsStore.create({
			notification: {
				type: "success",
				title: "Withdrawal accepted",
				description: `Transaction ${tx.hash.slice(0, 10)}... has been submitted.`,
				autoDestroy: true,
			},
		})

		await tx.wait(1)
		
		opConfirmationInProgress.value = false
		emit("onClose")
	} catch (error) {
		console.error("Withdrawal error:", error)
		notificationsStore.create({
			notification: {
				type: "error",
				title: "Something went wrong",
				description: error.message || "Please check your wallet and try again.",
				autoDestroy: true,
			},
		})
		opConfirmationInProgress.value = false
	}
}

const buttonState = computed(() => {
	if (opConfirmationInProgress.value)
		return {
			text: "Awaiting confirmation..",
			disabled: true,
			type: "secondary",
		}

	if (!availableClaims.value || !availableClaims.value.amount)
		return {
			text: "No balance to withdraw",
			disabled: true,
			type: "secondary",
		}

	return {
		text: `Confirm Withdrawal`,
		disabled: false,
		type: "primary",
	}
})
</script>

<template>
	<Modal new :show="show" width="550" closable @onClose="emit('onClose')">
		<Flex align="center" justify="between" :class="$style.head">
			<Flex align="center" gap="8">
				<Icon name="money" size="16" color="secondary" />

				<Text @click="emit('onBack')" size="14" weight="600" color="primary" :class="$style.head_btn"> Withdraw claims </Text>
			</Flex>

			<Icon @click="emit('onClose')" name="close" size="16" color="tertiary" :class="$style.close_icon" />
		</Flex>

		<Flex direction="column" gap="32" :class="$style.base">
			<!-- <Flex direction="column" gap="8">
				<Flex>
					<Text size="13" weight="500" color="tertiary" height="16">
						Your withdrawal request contains
						{{ availableClaims.length }} available claims. Funds will be available in your wallet as soon as all transactions
						are accepted.
					</Text>
				</Flex>
			</Flex> -->

			<Flex direction="column" gap="8">
				<Flex align="center" justify="between">
					<Text size="12" weight="600" color="secondary"> Withdrawal </Text>
					<!-- <Text size="12" weight="600" color="tertiary">
						{{ affectedPools.length }}
						affected
						{{ affectedPools.length > 1 ? "pools" : "pool" }}
					</Text> -->
				</Flex>

				<Flex align="center" justify="between" :class="$style.badge">
					<Flex align="center" gap="8">
						<Icon name="walletadd" size="14" color="green" />

						<Flex>
							<Text size="14" weight="600" color="primary">
								{{ numberWithSymbol(availableClaims.amount, ",") }}
							</Text>
							<Text size="14" weight="600" color="tertiary"> &nbsp;ꜩ </Text>
						</Flex>
					</Flex>

					<Text size="14" weight="600" color="tertiary">-></Text>

					<Flex align="center" gap="6">
						<div :class="$style.avatar_placeholder">
							<img :src="`https://services.tzkt.io/v1/avatars/${accountStore.pkh}`" alt="avatar" :class="$style.avatar" />
						</div>

						<Flex align="center">
							<Text size="14" weight="600" color="secondary">
								{{ shorten(accountStore.pkh) }}
							</Text>
						</Flex>
					</Flex>
				</Flex>
			</Flex>

			<Flex v-show="availableClaims && availableClaims.amount" direction="column" gap="16">
				<Flex direction="column" gap="8">
					<Flex align="center" justify="between" :class="$style.badge">
						<Flex align="center" gap="8">
							<Icon name="checkcircle" size="14" color="tertiary" />

							<Flex>
								<Text size="14" weight="600" color="primary"> Vault </Text>
								<Text size="14" weight="600" color="tertiary"> &nbsp;{{ vault?.name }} </Text>
							</Flex>
						</Flex>

						<Flex align="center" gap="8">
							<Icon name="banknote" size="14" color="tertiary" />

							<Flex>
								<Text size="14" weight="600" color="primary">
									{{ numberWithSymbol(availableClaims.amount, ",") }}
								</Text>
								<Text size="14" weight="600" color="tertiary"> &nbsp;ꜩ </Text></Flex
							>
						</Flex>
					</Flex>
				</Flex>
			</Flex>

			<Button
				@click="handleWithdraw"
				:type="buttonState.type"
				:disabled="buttonState.disabled"
				:loading="opConfirmationInProgress"
				size="large"
				block
			>
				<LoadingBar v-if="opConfirmationInProgress" size="16" />
				<template v-else>
					<Icon name="login" size="16" color="white" />
					{{ buttonState.text }}
				</template>
			</Button>
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
	padding: 0 20px 20px 20px;
}

.badge {
	height: 38px;

	border-radius: 8px;
	background: rgba(255, 255, 255, 0.05);

	padding: 0 12px;
}

.avatar {
	width: 20px;
	height: 20px;
	border-radius: 50%;
}

.avatar_placeholder {
	width: 20px;
	height: 20px;
	border-radius: 50%;
	background: var(--app-bg);
	color: #000;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 10px;
	font-weight: 700;
	text-transform: uppercase;
}
</style>
