<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from "vue"
import VaultStats from "./VaultStats.vue"
import VaultChart from "./VaultChart.vue"
import VaultDeposit from "./VaultDeposit.vue"
import VaultPersonalStats from "./VaultPersonalStats.vue"
import VaultEarnings from "./VaultEarnings.vue"
import VaultHistory from "./VaultHistory.vue"
import AgentActivity from "./AgentActivity.vue"
import VaultBaseLoading from "../../local/VaultCard/VaultBaseLoading.vue"
import Breadcrumbs from "@ui/Breadcrumbs.vue"
import Badge from "@ui/Badge.vue"
import Button from "@ui/Button.vue"
import DepositModal from "../../local/modals/pools/DepositModal.vue"
import WithdrawClaimsModal from "../../local/modals/pools/WithdrawClaimsModal.vue"
import { analytics, flameWager, initVaults } from "@sdk"
import { activeChainConfig } from "@config"
import { fetchVaultById } from "@/api/vaults"
import { fetchAgentLogs, fetchAgentTransactions, fetchAgentByVault } from "@/api/agent"
import { fetchUserStatistics } from "@/api/user"
import { useNotificationsStore } from "@store/notifications"
import { useAccountStore } from "@store/account"
import ConfigModal from "../../local/modals/shared/ConfigModal.vue"
import { 
  subscribeToAgentDecisions, 
  subscribeToAgentExecutions,
  subscribeToVault
} from "@/api/graphql/subscriptions"

const notificationsStore = useNotificationsStore()
const accountStore = useAccountStore()
const liveLogs = ref([])
const agentTransactions = ref([])
const subscriptions = []

const props = defineProps({
	id: String,
})

const vault = ref(null)
const isLoading = ref(true)
const activeTab = ref("info") // info | position

const showDepositModal = ref(false)
const showWithdrawModal = ref(false)
const showConfigModal = ref(false)
const agentConfig = ref(null)
const selectedAmount = ref(0)
const isWithdrawing = ref(false)
const userPosition = ref(null)

const breadcrumbs = computed(() => [
	{ name: "Explore", path: "/explore" },
	{ name: "Vaults", path: "/vaults" },
	{ name: vault.value ? vault.value.name : "Loading...", path: `/vaults/${props.id}` },
])

const mockPosition = computed(() => ({
	tvl: 3.25,
	returning: 3.37,
	potential: 0.12,
	symbol: vault.value?.token1?.symbol || activeChainConfig.nativeCurrency.symbol
}))

const fetchBackendData = async () => {
	try {
		const [logs, txs] = await Promise.all([
			fetchAgentLogs(),
			fetchAgentTransactions()
		])
		liveLogs.value = logs
		agentTransactions.value = txs
	} catch (error) {
		console.error("Failed to fetch backend data:", error)
	}
}

/**
 * Fetch real user statistics (indexed + on-chain)
 */
const fetchPositionData = async () => {
    const address = flameWager.address || accountStore.pkh
    if (!address || !vault.value) return
    
    try {
        initVaults([vault.value])
        
        const stats = await fetchUserStatistics(address, vault.value.address)
        userPosition.value = stats
    } catch (err) {
        console.error("[VaultBase] Failed to fetch user position:", err)
    }
}

watch(() => [flameWager.signer, vault.value?.address], async ([signer, newVaultAddr]) => {
	if (signer && newVaultAddr) {
		await fetchPositionData()
	}
}, { immediate: true })

const handleShowConfig = async () => {
    try {
        const agent = await fetchAgentByVault(props.id)
        if (agent) {
            agentConfig.value = agent.strategyConfig || {}
            showConfigModal.value = true
        } else {
            notificationsStore.create({
                notification: {
                    type: "warning",
                    title: "Agent not found",
                    description: "This vault doesn't have an active strategist yet.",
                    autoDestroy: true,
                },
            })
        }
    } catch (error) {
        console.error("Failed to fetch agent config:", error)
    }
}

const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    notificationsStore.create({
        notification: {
            type: "success",
            title: "Link copied",
            description: "Vault link copied to clipboard",
            autoDestroy: true,
        },
    })
}

onMounted(async () => {
	analytics.log("onPage", { name: "VaultDetail", id: props.id })
	try {
		await new Promise(r => setTimeout(r, 500))
		const data = await fetchVaultById(props.id)
		vault.value = data
		await fetchBackendData()
		await fetchPositionData()

    // Subscriptions
    subscriptions.push(subscribeToAgentDecisions((newLogs) => {
      fetchAgentLogs().then(logs => liveLogs.value = logs)
    }))

    subscriptions.push(subscribeToAgentExecutions((newTxs) => {
      fetchAgentTransactions().then(txs => agentTransactions.value = txs)
    }))

    subscriptions.push(subscribeToVault(props.id, (updatedVault) => {
      if (updatedVault) {
        const latestSnapshot = updatedVault.snapshots[0] || {}
        vault.value = {
          ...vault.value,
          tvl: latestSnapshot.totalAssets || 0,
          apy: latestSnapshot.apy || 0
        }
      }
    }))

	} catch (error) {
		console.error("Failed to fetch vault details:", error)
	} finally {
		isLoading.value = false
	}
})

onUnmounted(() => {
  subscriptions.forEach(sub => sub.unsubscribe())
})
</script>

<template>
	<div :class="$style.wrapper">
		<Breadcrumbs :crumbs="breadcrumbs" :class="$style.breadcrumbs" />

		<VaultBaseLoading v-if="isLoading" />

		<Flex v-else-if="vault" direction="column" gap="32">
			<!-- Header -->
			<Flex justify="between" align="center" wrap="wrap" gap="20">
				<Flex direction="column" gap="8">
					<Flex align="center" gap="12">
						<h1>{{ vault.name }}</h1>
						<Badge color="green" size="small">Active</Badge>
					</Flex>
					<Text size="14" weight="500" color="tertiary">{{ vault.strategyType }} • {{ vault.poolData?.dex }}</Text>
				</Flex>
				<Flex gap="12">
					<Button @click="handleShare" type="secondary" size="small">
						<Icon name="share" size="14" />
						Share
					</Button>
					<Button @click="handleShowConfig" type="secondary" size="small">
						<Icon name="settings" size="14" />
						Strategy Config
					</Button>
				</Flex>
			</Flex>

			<!-- Stats Row -->
			<VaultStats :vault="vault" />

			<!-- Content Tabs -->
			<div :class="$style.content_wrapper">
				<div :class="$style.tabs_header">
					<div 
						@click="activeTab = 'info'" 
						:class="[$style.content_tab, activeTab === 'info' && $style.active]"
					>
						Vault Information
					</div>
					<div 
						@click="activeTab = 'position'" 
						:class="[$style.content_tab, activeTab === 'position' && $style.active]"
					>
						Your Position
					</div>
				</div>

				<div :class="$style.grid">
					<div :class="$style.left">
						<!-- Vault Info Tab -->
						<template v-if="activeTab === 'info'">
							<Flex direction="column" gap="24">
								<VaultChart :vault="vault" />

								<!-- Strategy Activity (Refactored) -->
								<AgentActivity 
									:logs="liveLogs" 
									:transactions="agentTransactions"
									:pools="vault.vaultsPools"
								/>
							</Flex>
						</template>

						<template v-else>
							<Flex direction="column" gap="24">
								<!-- Your Position Stats -->
								<VaultPersonalStats :vault="vault" :position="userPosition" />

								<!-- Your Earnings Chart -->
								<VaultEarnings :vault="vault" />

								<!-- Transaction History -->
								<VaultHistory :vault="vault" />
							</Flex>
						</template>
					</div>

					<div :class="$style.right">
						<VaultDeposit 
							:vault="vault"
							:userPosition="userPosition"
							@onDeposit="(val) => { selectedAmount = val; showDepositModal = true }"
							
							@onWithdraw="showWithdrawModal = true"
						/>
					</div>
				</div>
			</div>
		</Flex>

		<!-- Modals -->
		<DepositModal 
			v-if="vault"
			:show="showDepositModal" 
			:initialAmount="selectedAmount"
			:selectedPool="{ address: vault.address, name: vault.name, entryLockPeriod: 3600 }"
			:state="{ totalLiquidity: 100, sharePrice: 1.05 }"
			:apy="8.5"
			@onClose="showDepositModal = false"
		/>

		<WithdrawClaimsModal 
			v-if="vault"
			:show="showWithdrawModal" 
			:vault="vault"
			:position="userPosition"
			@onClose="showWithdrawModal = false"
		/>

		<ConfigModal 
			v-if="vault"
			:show="showConfigModal"
			:title="`${vault.name} Strategy`"
			:config="agentConfig"
			@onClose="showConfigModal = false"
		/>
	</div>
</template>

<style module>
.wrapper {
	max-width: 1250px;
}

.breadcrumbs {
	margin-bottom: 24px;
}

.content_wrapper {
	display: flex;
	flex-direction: column;
	gap: 24px;
}

.tabs_header {
	display: flex;
	gap: 32px;
	border-bottom: 1px solid var(--border);
}

.content_tab {
	padding: 12px 0;
	font-size: 15px;
	font-weight: 600;
	color: var(--text-tertiary);
	cursor: pointer;
	position: relative;
	transition: color 0.2s;
}

.content_tab:hover {
	color: var(--text-secondary);
}

.content_tab.active {
	color: var(--text-primary);
}

.content_tab.active::after {
	content: "";
	position: absolute;
	bottom: -1px;
	left: 0;
	right: 0;
	height: 2px;
	background: var(--brand);
}

.grid {
	display: grid;
	grid-template-columns: 1fr 340px;
	gap: 24px;
}

.card {
	padding: 24px;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
}

.card_title {
	margin-bottom: 24px;
}

.pool_item {
	padding: 12px;
	background: var(--surface-02);
	border-radius: 8px;
}

.pool_icon {
	width: 24px;
	height: 24px;
	background: var(--border);
	border-radius: 50%;
}

.logs {
	margin-top: 16px;
	background: #000;
	padding: 16px;
	border-radius: 8px;
	font-family: 'JetBrains Mono', monospace;
	font-size: 12px;
	max-height: 200px;
	overflow-y: auto;
}

.log_line {
	margin-bottom: 4px;
	color: #fff;
}

.log_time {
	color: #666;
	margin-right: 8px;
}

.log_msg {
	color: #4ade80;
}

/* Stats Grid for Position */
.stats_grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20px;
}

.stat_item {
	display: flex;
	align-items: center;
	gap: 12px;
}

.stat_icon {
	width: 36px;
	height: 36px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: var(--surface-02);
}

.icon_blue { color: var(--blue); background: rgba(39, 110, 241, 0.1); }
.icon_green { color: var(--green); background: rgba(74, 222, 128, 0.1); }
.icon_orange { color: var(--orange); background: rgba(251, 146, 60, 0.1); }

.stat_label {
	letter-spacing: 0.05em;
	opacity: 0.8;
}

.history_card {
	padding: 0;
	overflow: hidden;
}

.history_card :global(.HistoryTable_wrapper__P7r_7) {
	padding: 24px;
}

.history_tabs {
	display: flex;
	gap: 24px;
	padding: 0 24px;
	border-bottom: 1px solid var(--border);
}

.history_tab {
	padding: 16px 0;
	font-size: 14px;
	font-weight: 700;
	color: var(--text-tertiary);
	cursor: pointer;
	position: relative;
	transition: color 0.2s;
}

.history_tab:hover {
	color: var(--text-secondary);
}

.history_tab.active {
	color: var(--text-primary);
}

.history_tab:active {
	transform: translateY(1px);
}

.history_tab.active::after {
	content: "";
	position: absolute;
	bottom: -1px;
	left: 0;
	right: 0;
	height: 2px;
	background: var(--brand);
}

/* Table styles */
.table_wrapper {
	overflow-x: auto;
}

.table {
	width: 100%;
	border-collapse: collapse;
}

.table th {
	text-align: left;
	font-size: 11px;
	font-weight: 700;
	color: var(--text-tertiary);
	padding: 0 0 12px 0;
	letter-spacing: 0.05em;
}

.table td {
	padding: 16px 0;
	border-top: 1px solid var(--border);
	font-size: 13px;
	font-weight: 600;
	color: var(--text-secondary);
}

.tx_icon {
	fill: var(--text-tertiary);
}

.tx_amount {
	color: var(--text-primary);
}

@media (max-width: 1000px) {
	.grid {
		grid-template-columns: 1fr;
	}

	.right {
		order: -1;
	}
}

.loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100px 0;
	gap: 20px;
}
</style>
