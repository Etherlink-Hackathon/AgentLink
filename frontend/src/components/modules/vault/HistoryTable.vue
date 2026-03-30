<script setup>
import { ref, computed } from "vue"
import Badge from "@ui/Badge.vue"
import Button from "@ui/Button.vue"
import Pagination from "@ui/Pagination.vue"
import { getCurrencyIcon } from "@utils/misc"

const props = defineProps({
	history: {
		type: Array,
		required: true,
	},
	mode: {
		type: String,
		default: "user", // user | agent
	}
})

const itemsPerPage = 5
const currentPage = ref(1)

const totalPages = computed(() => Math.ceil(props.history.length / itemsPerPage))

const paginatedHistory = computed(() => {
	const start = (currentPage.value - 1) * itemsPerPage
	const end = start + itemsPerPage
	return props.history.slice(start, end)
})

const getTxTypeColor = (type) => {
	switch (type.toLowerCase()) {
		case "deposit":
		case "arbitrage":
			return "green"
		case "withdraw request":
		case "swap":
			return "orange"
		case "withdraw cancelled":
			return "red"
		default:
			return "blue"
	}
}

const getExplorerUrl = (hash) => `https://explorer.etherlink.com/tx/${hash}`

const getTokenPair = (pair) => {
	if (!pair) return []
	return pair.split(" / ").map(t => t.trim().split(" ")[0])
}

</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.table_container">
			<table :class="$style.table">
				<thead>
					<tr>
						<th>TIMESTAMP</th>
						<th>TYPE</th>
						<th>PAIR</th>
						<th>DEX POOL</th>
						<th>AMOUNT</th>
						<th v-if="mode === 'agent'">PROFIT</th>
						<th :class="$style.align_right">EXPLORER</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(tx, index) in paginatedHistory" :key="index">
						<td>
							<Text size="13" weight="500" color="tertiary">{{ tx.timestamp }}</Text>
						</td>
						<td>
							<Flex align="center" gap="8">
								<div :class="[$style.type_dot, $style[getTxTypeColor(tx.type)]]" />
								<Text size="13" weight="600" color="secondary">{{ tx.type }}</Text>
							</Flex>
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
								<img v-if="tx.dex" :src="getCurrencyIcon(tx.dex)" :class="$style.dex_img" alt="dex" />
								<Text size="13" weight="600" color="secondary">{{ tx.dex || "—" }}</Text>
							</Flex>
						</td>
						<td>
							<Text size="13" weight="700" color="primary">{{ tx.amount }}</Text>
						</td>
						<td v-if="mode === 'agent'">
							<Text size="13" weight="700" :color="tx.profit.startsWith('+') ? 'green' : (tx.profit.startsWith('-') ? 'red' : 'primary')">
								{{ tx.profit }}
							</Text>
						</td>
						<td :class="$style.align_right">
							<a :href="getExplorerUrl(tx.hash)" target="_blank" :class="$style.explorer_link">
								<Icon name="external" size="14" />
							</a>
						</td>
					</tr>
					<tr v-if="history.length === 0">
						<td :colspan="mode === 'agent' ? 7 : 6" :class="$style.empty">
							No transactions found
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Pagination -->
		<Flex v-if="totalPages > 1" justify="center" align="center" :class="$style.pagination">
			<Pagination
				v-model="currentPage"
				:total="history.length"
				:limit="itemsPerPage"
			/>
		</Flex>
	</div>
</template>

<style module>
.wrapper {
	width: 100%;
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

.table th:first-child {
	padding-left: 0;
}

.table th:last-child {
	padding-right: 0;
}

.table td {
	padding: 16px 16px;
	border-top: 1px solid var(--border);
}

.table td:first-child {
	padding-left: 0;
}

.table td:last-child {
	padding-right: 0;
}

.align_right {
	text-align: right;
}

.type_dot {
	width: 8px;
	height: 8px;
	border-radius: 50%;
}

.type_dot.green { background: var(--green); }
.type_dot.orange { background: var(--orange); }
.type_dot.red { background: var(--red); }
.type_dot.blue { background: var(--blue); }

.explorer_link {
	display: inline-flex;
	padding: 6px;
	border-radius: 6px;
	background: var(--surface-02);
	color: var(--text-tertiary);
	transition: all 0.2s;
}

.explorer_link:hover {
	color: var(--text-primary);
	background: var(--surface-03);
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
</style>
