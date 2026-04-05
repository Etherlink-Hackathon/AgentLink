<script setup>
/**
 * Vendor
 */
import { computed, onBeforeUnmount, onMounted, reactive } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import { DateTime } from "luxon"

/**
 * Services
 */
import { flameWager, switchNetwork, currentNetwork } from "@sdk"
import { capitalizeFirstLetter } from "@utils/misc"

/**
 * UI
 */
import Button from "@ui/Button.vue"
import Tooltip from "@ui/Tooltip.vue"
import { Dropdown, DropdownItem, DropdownTitle } from "@ui/Dropdown"

const router = useRouter()

/** Watch for Network */
let checkInterval = null

const STATUSES = {
	LOADING: "Loading..",
	GOOD: "Good",
	DELAYED: "Delayed",
}

const status = reactive({
	network: STATUSES.LOADING,
	dipdup: STATUSES.LOADING,
})

const statusBlock = computed(() => {
	if (status.dipdup === STATUSES.GOOD && status.network === STATUSES.GOOD) {
		return { text: "Stable", color: "green" }
	} else if (status.dipdup === STATUSES.DELAYED && status.network === STATUSES.DELAYED) {
		return { text: "Everything delayed", color: "red" }
	} else {
		return { text: "Systems delayed", color: "yellow" }
	}
})

const checkDipdup = async () => {
	const graphqlUrl = import.meta.env.VITE_GRAPHQL_URL || "http://localhost:8181/v1/graphql"
	const url = graphqlUrl.replace("/v1/graphql", "")

	if (!url) {
		status.dipdup = STATUSES.GOOD
		return
	}

	try {
		await axios.get(url)
		status.dipdup = STATUSES.GOOD
	} catch (e) {
		status.dipdup = STATUSES.DELAYED
	}
}

const checkNetwork = async () => {
	const rpcUrl =
		currentNetwork.value === "mainnet" ? "https://node.mainnet.etherlink.com" : "https://node.shadownet.etherlink.com"

	try {
		const { data } = await axios.post(rpcUrl, {
			jsonrpc: "2.0",
			method: "eth_getBlockByNumber",
			params: ["latest", false],
			id: 1,
		})

		if (data.result && data.result.timestamp) {
			const networkDt = DateTime.fromSeconds(parseInt(data.result.timestamp, 16))
			const networkDiff = DateTime.now().diff(networkDt, ["minutes", "seconds"]).toObject()

			if (networkDiff.minutes >= 1) {
				status.network = STATUSES.DELAYED
			} else {
				status.network = STATUSES.GOOD
			}
		}
	} catch (e) {
		status.network = STATUSES.DELAYED
	}
}

const handleSwitch = (network) => {
  switchNetwork(network, router)
}

onMounted(async () => {
	checkDipdup()
	checkNetwork()

	checkInterval = setInterval(async () => {
		checkDipdup()
		checkNetwork()
	}, 30000)
})

onBeforeUnmount(() => {
	clearInterval(checkInterval)
})
</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.base">
			<div :class="$style.content">
				<div :class="$style.logo">
					<Icon name="logo_symbol" size="32" viewBox="0 0 100 100"/>
				</div>

				<div :class="$style.columns">
					<div :class="$style.column">
						<div :class="$style.name">AgentLink</div>

						<router-link to="/explore" :class="$style.link">Explore</router-link>
						<router-link to="/vaults" :class="$style.link">Vaults</router-link>
					</div>

					<div :class="$style.column">
						<div :class="$style.name">Learn</div>
						<router-link to="/docs" :class="$style.link">Documentation</router-link>
						<router-link to="/docs" :class="$style.link">Roadmap</router-link>
						<router-link to="/docs" :class="$style.link">FAQ</router-link>
					</div>

					<div :class="$style.column">
						<div :class="$style.name">Legal</div>
						<router-link to="/policy" :class="$style.link">Privacy Policy</router-link>
						<router-link to="/terms" :class="$style.link">Terms of Use</router-link>
					</div>
				</div>
			</div>

			<div :class="$style.bottom">
				<div :class="$style.block">
					<div :class="$style.left">
						<Tooltip placement="top">
							<Button
								type="secondary"
								size="small"
								link="https://status.wager.com"
								:class="[$style.footer_btn, $style[statusBlock.color]]"
							>
								<Icon :name="(statusBlock.color === 'green' && 'checkcircle') || 'warning'" size="14" :class="$style" />
								{{ statusBlock.text }}
							</Button>

							<template #content>
								<span>DipDup:</span> {{ status.dipdup }}<br /><span>Network:</span> {{ status.network }}<br />
							</template>
						</Tooltip>

						<Dropdown side="top">
							<template #trigger>
								<Button type="secondary" size="small" :class="[$style.footer_btn]" data-cy="network-dropdown">
									<Icon :name="currentNetwork === 'testnet' ? 'hammer' : 'explorer'" size="12" />
									{{ currentNetwork === "mainnet" ? "Main Network" : "Test Network" }}
									<Icon name="arrow" size="12" />
								</Button>
							</template>

							<template #dropdown>
								<DropdownTitle>Network</DropdownTitle>
								<DropdownItem @click="handleSwitch('mainnet')" :data-active="currentNetwork === 'mainnet' && true"
									><Icon :name="currentNetwork === 'mainnet' ? 'check' : 'dot'" size="16" />
									Main Network
								</DropdownItem>
								<DropdownItem @click="handleSwitch('testnet')" :data-active="currentNetwork === 'testnet' && true">
									<Icon :name="currentNetwork === 'testnet' ? 'check' : 'dot'" size="16" />
									Test Network
								</DropdownItem>
							</template>
						</Dropdown>
					</div>

					<div :class="$style.right">
						<Button type="secondary" size="small" link="https://x.com/wagerEtherlink" target="_blank" :class="$style.footer_btn">
							X
							<Icon name="arrowrighttop" size="16" color="tertiary" />
						</Button>
					</div>
				</div>

				<Flex justify="between" :class="$style.copyrights">
					<Flex align="center" wrap="wrap" :class="$style.line">
						<Text size="14" weight="500" color="tertiary"> © {{ DateTime.now().year }}&nbsp;&nbsp; </Text>
						<Text size="11" color="support">✦</Text>
						<Text size="14" weight="500" color="secondary"> &nbsp;&nbsp;AgentLink&nbsp; </Text>
						<Text size="14" weight="500" color="tertiary"> Powered by&nbsp; </Text>
						<a href="https://explorer.etherlink.com" target="_blank">
							<Text size="14" weight="500" color="secondary"> Etherlink </Text>
						</a>
					</Flex>

					<Flex direction="column" gap="8" align="end" :class="$style.line">
						<Text size="12" weight="500" color="support">
							Trading and investing in digital assets involves significant risk and may result in the loss of your invested capital. 
						</Text>
						<Text size="12" weight="500" color="support"> You should ensure that you fully understand the risk involved and take into account your level of experience. </Text>
					</Flex>
				</Flex>
			</div>
		</div>
	</div>
</template>

<style module>
.wrapper {
	width: 100%;

	display: flex;
	justify-content: center;

	border-top: 1px solid var(--border);
}

.base {
	width: 100%;
	max-width: 1250px;
	margin: 0 32px;
	padding: 50px 0;
}

.content {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: 60px;
}

.logo {
	display: flex;
	align-items: center;
	gap: 12px;

	fill: var(--text-support);
}

.columns {
	display: flex;
	flex-wrap: wrap;
	gap: 150px;
}

.column {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.name {
	font-size: 14px;
	font-weight: 600;
	color: var(--text-primary);
}

.link {
	font-size: 14px;
	font-weight: 500;
	color: var(--text-tertiary);

	transition: color 0.2s ease;
}

.link:hover {
	color: var(--text-primary);
}

.link:focus {
	box-shadow: 0 0 0 transparent;
	color: var(--text-primary);
}

.bottom {
	display: flex;
	flex-direction: column;
	gap: 24px;

	margin-top: 50px;
}

.block {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.left,
.right {
	display: flex;
	align-items: center;
	gap: 8px;
}

.footer_btn {
	color: var(--text-secondary);
}

.footer_btn.green svg {
	fill: var(--green);
}

.footer_btn.yellow svg {
	fill: var(--yellow);
}

.footer_btn.red svg {
	fill: var(--red);
}

@media (max-width: 900px) {
	.content {
		flex-direction: column;
		align-items: center;
	}

	.block {
		flex-direction: column;
		gap: 24px;
	}

	.copyrights {
		flex-wrap: wrap;
		justify-content: center;

		gap: 24px;
	}

	.line {
		align-items: center;
		justify-content: center;
	}

	.line * {
		text-align: center;
		line-height: 1.6;
	}
}

@media (max-width: 700px) {
	.columns {
		gap: 50px;
		flex-direction: column;
	}

	.column {
		align-items: center;
	}
}
</style>
