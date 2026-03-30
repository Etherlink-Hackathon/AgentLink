<script setup>
import { ref } from "vue"
import HistoryTable from "./HistoryTable.vue"
import Badge from "@ui/Badge.vue"

const props = defineProps({
	logs: Array,
	transactions: Array,
})

const activeTab = ref("logs") // logs | txs
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
				<Badge v-if="activeTab === 'logs'" color="blue" size="small">Streaming</Badge>
			</Flex>
		</div>

		<div :class="$style.content">
			<!-- Execution Logs -->
			<div v-if="activeTab === 'logs'" :class="$style.logs">
				<div v-for="(log, i) in logs" :key="i" :class="$style.log_line">
					<span :class="$style.log_time">{{ log.time }}</span>
					<span :class="$style.log_msg">{{ log.msg }}</span>
				</div>
				<div v-if="logs.length === 0" :class="$style.empty_logs">
					Waiting for agent to start...
				</div>
			</div>

			<!-- Agent Transactions -->
			<div v-else :class="$style.transactions">
				<HistoryTable :history="transactions" mode="agent" />
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

/* HistoryTable Overrides */
.transactions :global(.HistoryTable_wrapper__P7r_7) {
	padding: 0;
}
</style>
