<script setup>
import { ref } from "vue"
import HistoryTable from "./HistoryTable.vue"

const props = defineProps({
	vault: Object,
})

const mockHistory = [
	{ 
		type: "Deposit", 
		amount: "1.50 XTZ", 
		timestamp: "Nov 23, 2025 10:42 AM", 
		hash: "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" 
	},
	{ 
		type: "Withdraw Request", 
		amount: "0.25 XTZ", 
		timestamp: "Nov 21, 2025 02:15 PM", 
		hash: "0x89221f1912252a3b844Bc454e4438f44e12345678" 
	},
	{ 
		type: "Deposit", 
		amount: "2.00 XTZ", 
		timestamp: "Nov 19, 2025 09:30 AM", 
		hash: "0x1234567890abcdef1234567890abcdef12345678" 
	},
	{ 
		type: "Withdraw Cancelled", 
		amount: "0.50 XTZ", 
		timestamp: "Nov 17, 2025 08:05 PM", 
		hash: "0xabcdef1234567890abcdef1234567890abcdef12" 
	},
	{ 
		type: "Deposit", 
		amount: "1.00 XTZ", 
		timestamp: "Nov 15, 2025 11:20 AM", 
		hash: "0x9876543210fedcba9876543210fedcba98765432" 
	},
]
</script>

<template>
	<div :class="$style.wrapper">
		<Flex justify="between" align="center" :class="$style.header">
			<Text size="14" weight="600" color="primary">Your Transactions</Text>
			
			<div :class="$style.filter">
				<Text size="12" weight="600" color="tertiary">Filter</Text>
				<Icon name="arrow" size="12" color="tertiary" />
			</div>
		</Flex>

		<HistoryTable :history="mockHistory" />
	</div>
</template>

<style module>
.wrapper {
	padding: 24px;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
}

.header {
	margin-bottom: 24px;
}

.filter {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 6px 12px;
	background: var(--surface-02);
	border-radius: 8px;
	border: 1px solid var(--border);
	cursor: pointer;
	transition: all 0.2s;
}

.filter:hover {
	background: var(--surface-03);
	border-color: var(--opacity-20);
}

.filter :global(svg) {
	transform: rotate(0deg);
}
</style>
