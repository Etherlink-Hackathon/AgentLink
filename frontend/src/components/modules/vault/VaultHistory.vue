<script setup>
import { ref, onMounted, computed } from "vue"
import { useAccountStore } from "@/store/account"
import { fetchUserActions } from "@/api/user"
import { DateTime } from "luxon"
import HistoryTable from "./HistoryTable.vue"

const props = defineProps({
	vault: Object,
})

const account = useAccountStore()
const history = ref([])
const isLoading = ref(false)

const mappedHistory = computed(() => {
	return history.value.map(action => ({
		id: action.id,
		type: action.type,
		amount: `${parseFloat(action.assets).toFixed(4)} XTZ`, 
		timestamp: DateTime.fromISO(action.timestamp).toFormat("MMM dd, yyyy HH:mm"),
		hash: action.hash
	}))
})

onMounted(async () => {
	if (account.pkh && props.vault?.address) {
		isLoading.value = true
		try {
			const data = await fetchUserActions(account.pkh.toLowerCase(), props.vault.address)
			history.value = data
		} catch (error) {
			console.error("Failed to fetch history:", error)
		} finally {
			isLoading.value = false
		}
	}
})
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

		<HistoryTable :history="mappedHistory" />
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
