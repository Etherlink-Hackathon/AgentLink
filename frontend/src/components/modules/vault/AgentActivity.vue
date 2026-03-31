<script setup>
import { ref, computed } from "vue"
import Pagination from "@ui/Pagination.vue"
import { getCurrencyIcon, getDexIcon } from "@utils/misc"
import { DateTime } from "luxon"

const props = defineProps({
	logs: Array,
	transactions: Array,
})

const activeTab = ref("logs") // logs | txs

const itemsPerPage = 5
const currentPage = ref(1)

const totalPages = computed(() => {
	if (!props.transactions) return 0
	return Math.ceil(props.transactions.length / itemsPerPage)
})

const formatLogTime = (ts) => {
	return DateTime.fromISO(ts).toFormat("HH:mm:ss")
}

const formatTxTime = (ts) => {
	return DateTime.fromISO(ts).toFormat("MMM dd, HH:mm")
}

const getLogMessage = (log) => {
	if (log.status === "error") return `Error: ${log.error}`
	if (log.geminiVerdict === "EXECUTE") return `🚀 Gemini detected opportunity! Executing swap...`
	if (log.heuristicsVerdict === "EXECUTE") return `⚡ Heuristics triggered scan. Found profitable route.`
	return `🔍 Scanning pools... ${log.status}`
}

const paginatedHistory = computed(() => {
	if (!props.transactions) return []
	const mapped = props.transactions.map(tx => {
		const firstHop = tx.routeDetails?.steps?.[0] || {}
		return {
			...tx,
			time: formatTxTime(tx.timestamp),
			pair: firstHop.token_in ? `${firstHop.token_in} / ${firstHop.token_out}` : "Multi-hop",
			dex: firstHop.dex || "Oku Trade",
			type: "Arbitrage",
			direction: "Execution",
			size: firstHop.amount_in ? `${parseFloat(firstHop.amount_in).toFixed(4)} ${firstHop.token_in}` : "—",
			profit: tx.profit ? `${parseFloat(tx.profit) > 0 ? '+' : ''}${parseFloat(tx.profit).toFixed(6)}` : "0.00"
		}
	})

	const start = (currentPage.value - 1) * itemsPerPage
	const end = start + itemsPerPage
	return mapped.slice(start, end)
})

const getExplorerUrl = (hash) => `https://explorer.etherlink.com/tx/${hash}`

const getTokenPair = (pair) => {
	if (!pair) return []
	return pair.split(" / ").map(t => t.trim().split(" ")[0])
}
</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.card_header">
			<Flex justify="between" align="center">
				<Flex gap="24">
					<div 
						@click="activeTab = 'logs'" 
						:class="[$style.tab, activeTab === 'logs' && $style.active]"
					>
						Execution Log
					</div>
					<div 
						@click="activeTab = 'txs'" 
						:class="[$style.tab, activeTab === 'txs' && $style.active]"
					>
						Agent Transactions
					</div>
				</Flex>
			</Flex>
		</div>

		<div :class="$style.content">
			<!-- Execution Logs -->
			<div v-if="activeTab === 'logs'" :class="$style.logs">
				<div v-for="(log, i) in logs" :key="i" :class="$style.log_line">
					<span :class="$style.log_time">{{ formatLogTime(log.createdAt) }}</span>
					<span :class="$style.log_msg">{{ getLogMessage(log) }}</span>
				</div>
				<div v-if="logs.length === 0" :class="$style.empty_logs">
					Waiting for agent to start...
				</div>
			</div>

			<!-- Agent Transactions -->
			<div v-else :class="$style.transactions">
				<div :class="$style.table_container">
					<table :class="$style.table">
						<thead>
							<tr>
								<th>TIME</th>
								<th>PAIR</th>
								<th>DEX</th>
								<th>TYPE</th>
								<th>DIRECTION</th>
								<th>SIZE</th>
								<th>PROFIT</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="(tx, index) in paginatedHistory" :key="index">
								<td>
									<a :href="getExplorerUrl(tx.hash)" target="_blank" :class="$style.time_link">
										{{ tx.time }}
										<Icon name="external" size="14" :class="$style.external_icon" />
									</a>
								</td>
								<td>
									<Flex align="center" gap="8">
										<div v-if="tx.pair" :class="$style.pair_imgs">
											<img :src="getCurrencyIcon(getTokenPair(tx.pair)[0])" alt="symbol" />
											<img :src="getCurrencyIcon(getTokenPair(tx.pair)[1])" alt="symbol" />
										</div>
										<Text size="13" weight="600" color="primary">{{ tx.pair || "—" }}</Text>
									</Flex>
								</td>
								<td>
									<Flex align="center" gap="8">
										<img v-if="tx.dex" :src="getDexIcon(tx.dex)" :class="$style.dex_img" alt="dex" />
										<Text size="13" weight="600" color="secondary">{{ tx.dex || "—" }}</Text>
									</Flex>
								</td>
								<td>
									<Text size="13" weight="600" :color="tx.type === 'Limit' ? 'green' : 'secondary'">{{ tx.type }}</Text>
								</td>
								<td>
									<Text size="13" weight="600" :color="tx.direction === 'Buy' ? 'green' : 'red'">{{ tx.direction }}</Text>
								</td>
								<td>
									<Text size="13" weight="600" color="primary">{{ tx.size }}</Text>
								</td>
								<td>
									<Text size="13" weight="700" :color="tx.profit.startsWith('+') ? 'green' : (tx.profit.startsWith('-') ? 'red' : 'primary')">
										{{ tx.profit }}
									</Text>
								</td>
							</tr>
							<tr v-if="!transactions || transactions.length === 0">
								<td colspan="7" :class="$style.empty">
									No transactions found
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<Flex v-if="totalPages > 1" justify="center" align="center" :class="$style.pagination">
					<Pagination
						v-model="currentPage"
						:total="transactions.length"
						:limit="itemsPerPage"
					/>
				</Flex>
			</div>
		</div>
	</div>
</template>

<style module>
.wrapper {
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
	overflow: hidden;
}

.card_header {
	padding: 0 24px;
	border-bottom: 1px solid var(--border);
}

.tab {
	padding: 16px 0;
	font-size: 14px;
	font-weight: 600;
	color: var(--text-tertiary);
	cursor: pointer;
	position: relative;
	transition: color 0.2s;
}

.tab:hover {
	color: var(--text-secondary);
}

.tab.active {
	color: var(--text-primary);
}

.tab.active::after {
	content: "";
	position: absolute;
	bottom: -1px;
	left: 0;
	right: 0;
	height: 2px;
	background: var(--brand);
}

.content {
	padding: 24px;
}

.logs {
	background: #000;
	padding: 20px;
	border-radius: 8px;
	font-family: 'JetBrains Mono', monospace;
	font-size: 13px;
	line-height: 1.6;
	max-height: 300px;
	overflow-y: auto;
	box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
}

.log_line {
	margin-bottom: 6px;
	color: #fff;
}

.log_time {
	color: #666;
	margin-right: 12px;
	user-select: none;
}

.log_msg {
	color: #4ade80;
}

.empty_logs {
	color: var(--text-tertiary);
	font-style: italic;
	text-align: center;
	padding: 20px;
}

.transactions {
	min-height: 200px;
}

.table_container {
	width: 100%;
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
	padding: 16px 16px;
	letter-spacing: 0.05em;
	text-transform: uppercase;
}

.table td {
	padding: 16px 16px;
	border-top: 1px solid var(--border);
	white-space: nowrap;
}

.table th:first-child,
.table td:first-child {
	padding-left: 0;
}

.table th:last-child,
.table td:last-child {
	padding-right: 0;
}

.empty {
	text-align: center;
	padding: 40px 0;
	color: var(--text-tertiary);
	font-style: italic;
}

.pagination {
	margin-top: 16px;
	padding-top: 16px;
	border-top: 1px solid var(--border);
}

.pair_imgs {
	position: relative;
	width: 24px;
	height: 16px;
	flex-shrink: 0;
}

.pair_imgs img {
	width: 16px;
	height: 16px;
	border-radius: 5px;
}

.pair_imgs img:first-child {
	position: absolute;
	z-index: 1;
	left: 0;
	outline: 2px solid var(--card-bg);
	background: var(--card-bg);
}

.pair_imgs img:last-child {
	position: absolute;
	right: 0;
}

.dex_img {
	width: 16px;
	height: 16px;
	border-radius: 5px;
	flex-shrink: 0;
}

.time_link {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	font-size: 13px;
	font-weight: 500;
	color: var(--text-tertiary);
	text-decoration: none;
	cursor: pointer;
	position: relative;
}

.time_link:hover {
	color: var(--text-primary);
	text-decoration: underline;
}

.external_icon {
	color: var(--text-tertiary);
	transition: color 0.2s ease;
}

.time_link:hover .external_icon {
	color: var(--text-primary);
}
</style>
