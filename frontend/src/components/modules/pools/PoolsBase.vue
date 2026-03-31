<script setup>
/**
 * Vendor
 */
import { ref, onMounted, computed } from "vue"
import { useMeta } from "vue-meta"

/**
 * Local
 */
import MyFunds from "./MyFunds.vue"
import MyStatistics from "./MyStatistics.vue"
import BottomInfo from "./BottomInfo.vue"
import PoolsStats from "./PoolsStats.vue"
import PoolsList from "./PoolsList.vue"

/**
 * UI
 */
import Block from "@ui/Block.vue"

/**
 * Modal
 */
import SharePoolModal from "@local/modals/pools/SharePoolModal.vue"
import PoolsModal from "@local/modals/pools/PoolsModal.vue"
import DepositModal from "@local/modals/pools/DepositModal.vue"
import RequestWithdrawModal from "@local/modals/pools/RequestWithdrawModal.vue"
import WithdrawClaimsModal from "@local/modals/pools/WithdrawClaimsModal.vue"
import TimelineModal from "@local/modals/pools/TimelineModal.vue"

/**
 * Services
 */
import { flags, updateFlag } from "@/services/flags"

/**
 * API
 */
import { fetchPools } from "@/api/pools"

/**
 * Store
 */
import { useAccountStore } from "@store/account"
import { useNotificationsStore } from "@store/notifications"

const accountStore = useAccountStore()
const notificationsStore = useNotificationsStore()

const showSharePoolModal = ref(false)
const showPoolsModal = ref(false)
const showTimelineModal = ref(false)
const showDepositModal = ref(false)
const showWithdrawClaimsModal = ref(false)
const showRequestWithdrawModal = ref(false)

const pools = ref([])
const isPopulated = ref(false)
const selectedPool = ref({})

const handleSelectPool = (pool) => {
	selectedPool.value = pool
	showPoolsModal.value = false
	showDepositModal.value = true
}

const handleShare = (pool) => {
	selectedPool.value = pool
	showSharePoolModal.value = true
}

const handleRequestWithdraw = (pool) => {
	selectedPool.value = pool
	showRequestWithdrawModal.value = true
}

const handleBackFromDeposit = () => {
	showDepositModal.value = false
	showPoolsModal.value = true
}

const handleWatchEvents = (pool) => {
	selectedPool.value = pool
	showTimelineModal.value = true
}

const handleClosePoolsWarning = () => {
	updateFlag("showGeneralPoolsWarning", false)

	notificationsStore.create({
		notification: {
			type: "success",
			title: "Warning is now hidden",
			autoDestroy: true,
			actions: [
				{
					name: "Undo",
					icon: "back",
					callback: () => {
						updateFlag("showGeneralPoolsWarning", true)
					},
				},
			],
		},
	})
}

const populatePools = async () => {
	try {
        const data = await fetchPools()
        pools.value = data
        isPopulated.value = true
    } catch (error) {
        console.error("Failed to populate pools:", error)
    }
}

const showAnimation = ref(false)
onMounted(() => {
	showAnimation.value = true
	populatePools()
})

/** Meta */
const { meta } = useMeta({
	title: `Liquidity Pools`,
	description: "Liquidity Pools Management",
})
</script>

<template>
	<transition name="slide">
		<div v-if="showAnimation" :class="$style.wrapper">
			<metainfo>
				<template v-slot:title="{ content }">{{ content }} • Juster</template>
			</metainfo>

			<!-- Modals -->
			<SharePoolModal :show="showSharePoolModal" :pool="selectedPool" @onClose="showSharePoolModal = false" />
			<PoolsModal
				v-if="pools.length"
				:show="showPoolsModal"
				:pools="pools"
				:poolsStates="poolsStates"
				:poolsAPY="poolsAPY"
				@onSelectPool="handleSelectPool"
				@onClose="showPoolsModal = false"
			/>
			<DepositModal
				:show="showDepositModal"
				:selectedPool="selectedPool"
				:state="poolsStates[selectedPool.address]"
				:apy="poolsAPY[selectedPool.address]"
				@onBack="handleBackFromDeposit"
				@onClose="showDepositModal = false"
			/>
			<RequestWithdrawModal
				:show="showRequestWithdrawModal"
				:selectedPool="selectedPool"
				:state="poolsStates[selectedPool.address]"
				:position="positions.find((pos) => pos.poolId === selectedPool.address)"
				@onClose="showRequestWithdrawModal = false"
			/>
			<WithdrawClaimsModal :show="showWithdrawClaimsModal" :positions="positions" @onClose="showWithdrawClaimsModal = false" />
			<TimelineModal :show="showTimelineModal" :pool="selectedPool" @onClose="showTimelineModal = false" />

			<Flex align="center" :class="$style.head">
				<h1 :class="$style.title">Liquidity Pools</h1>
			</Flex>

			<Flex justify="between" :class="$style.content">
				<Flex direction="column" gap="24" :class="$style.side">
					<MyFunds
						:pools="pools"
						:poolsStates="poolsStates"
						:entries="entries"
						:positions="positions"
						:summaries="summaries"
						:isReady="isPopulated"
						@onManualEntryApprove="handleManualEntryApprove"
						@onDepositLiquidity="showPoolsModal = true"
						@onGetClaims="showWithdrawClaimsModal = true"
					/>

					<MyStatistics
						v-if="accountStore.pkh"
						:positions="positions"
						:poolsAPY="poolsAPY"
						:poolsStates="poolsStates"
						:summaries="summaries"
						:isReady="isPopulated"
					/>

					<BottomInfo v-if="pools.length" :pool="pools[0]" :class="$style.bottom_left_block" />
				</Flex>

				<Flex direction="column" gap="24" wide :class="$style.base">
					<PoolsStats :pools="pools" :poolsStates="poolsStates" :poolsAPY="poolsAPY" />

					<Block v-if="flags.showGeneralPoolsWarning" @onClose="handleClosePoolsWarning">
						<span>Current APYs is approximate.</span> Values may change over the next few months. Planning for long-term income
						based on these values may differ from the actual.
					</Block>

					<transition name="fade">
						<PoolsList
							v-if="pools.length"
							:pools="pools"
							:poolsStates="poolsStates"
							:poolsAPY="poolsAPY"
							:positions="positions"
							@onShare="(pool) => handleShare(pool)"
							@onSelectPool="handleSelectPool"
							@onWatchEvents="(pool) => handleWatchEvents(pool)"
							@onRequestWithdraw="handleRequestWithdraw"
							:class="$style.list"
						/>
					</transition>

					<BottomInfo v-if="pools.length" :pool="pools[0]" :class="$style.bottom_right_block" />
				</Flex>
			</Flex>
		</div>
	</transition>
</template>

<style module>
.wrapper {
}

.title {
	font-size: 16px;
}

.head {
	border-bottom: 1px solid var(--border);

	padding-bottom: 16px;
	margin-bottom: 24px;
}

.side {
	max-width: 450px;
}

.base {
	max-width: 760px;

	margin-left: 32px;
}

.list {
	margin-top: 32px;
}

.bottom_right_block {
	display: none;
}

@media (max-width: 1000px) {
	.content {
		flex-direction: column;

		gap: 40px;
	}

	.bottom_left_block {
		display: none;
	}

	.bottom_right_block {
		display: flex;
	}

	.side {
		max-width: initial;

		position: initial;
	}

	.base {
		margin: 0;
		max-width: initial;
	}
}
</style>
