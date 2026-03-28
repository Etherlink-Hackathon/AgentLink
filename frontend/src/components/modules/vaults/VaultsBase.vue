<script>
import { defineComponent, ref, reactive, computed, onMounted } from "vue"

/**
 * UI
 */
import Pagination from "@ui/Pagination.vue"
import Breadcrumbs from "@ui/Breadcrumbs.vue"
import Button from "@ui/Button.vue"

/**
 * Local
 */
import VaultsFilters from "./VaultsFilters.vue"
import { VaultCard, VaultCardLoading } from "@/components/local/VaultCard"

/**
 * Services
 */
import { analytics } from "@sdk"

/**
 * API
 */
import { fetchVaults } from "@/api/vaults"

export default defineComponent({
	name: "VaultsBase",

	setup() {
		const defaultFilters = {
			symbols: [
				{ name: "ETH", active: false },
				{ name: "WBTC", active: false },
				{ name: "XTZ", active: false },
				{ name: "USDC", active: false },
				{ name: "USDT", active: false },
				{ name: "LYZI", active: false },
				{ name: "TZPEPE", active: false },
				{ name: "mBASIS", active: false },
				{ name: "mTBILL", active: false },
			],
			statuses: [
				{ name: "New", active: false, icon: "event_new", color: "purple" },
				{ name: "Running", active: false, icon: "event_active", color: "yellow" },
				{ name: "Finished", active: false, icon: "event_finished", color: "green" },
			],
			dexs: [
				{ name: "V3Swap", active: false },
				{ name: "EtherlinkDex", active: false },
				{ name: "OmniPool", active: false },
			],
			strategies: [
				{ name: "Arbitrage", active: false },
				{ name: "Market Making", active: false },
				{ name: "Trend Following", active: false },
			],
			advanced: {
				liquidity: { min: 0, max: 100000 },
				participants: [],
				period: null,
			},
		}

		const filters = reactive(JSON.parse(JSON.stringify(defaultFilters)))
		const currentPage = ref(1)
		const showFilters = ref(false)

		const breadcrumbs = [
			{ name: "Explore", path: "/explore" },
			{ name: "Vaults", path: "/vaults" },
		]

		// Real data from API
		const allVaults = ref([])
		const isLoading = ref(true)

		const filteredVaults = computed(() => {
			return allVaults.value.filter((vault) => {
				// Symbol filter
				const activeSymbols = filters.symbols
					.filter((s) => s.active)
					.map((s) => s.name)
				const symbolMatch =
					activeSymbols.length === 0 ||
					activeSymbols.includes(vault.token0.symbol) ||
					activeSymbols.includes(vault.token1.symbol)

				// Status filter
				const activeStatuses = filters.statuses
					.filter((s) => s.active)
					.map((s) => s.name.toLowerCase())
				const statusMatch =
					activeStatuses.length === 0 ||
					activeStatuses.includes(vault.status.toLowerCase())

				// DEX filter
				const activeDexs = filters.dexs
					.filter((d) => d.active)
					.map((d) => d.name)
				const dexMatch =
					activeDexs.length === 0 || activeDexs.includes(vault.dex)

				return symbolMatch && statusMatch && dexMatch
			})
		})

		const paginatedVaults = computed(() => {
			const start = (currentPage.value - 1) * 4
			const end = start + 4
			return filteredVaults.value.slice(start, end)
		})

		const handleSelect = (category, item) => {
			const found = filters[category].find((i) => i.name === item.name)
			if (found) found.active = !found.active
		}

		const handleReset = () => {
			Object.assign(filters, JSON.parse(JSON.stringify(defaultFilters)))
		}

		onMounted(async () => {
			analytics.log("onPage", { name: "Vaults" })

			try {
				const data = await fetchVaults()
				allVaults.value = data
			} catch (error) {
				console.error("Failed to fetch vaults:", error)
			} finally {
				isLoading.value = false
			}
		})

		return {
			filters,
			currentPage,
			showFilters,
			breadcrumbs,
			allVaults,
			isLoading,
			filteredVaults,
			paginatedVaults,
			handleSelect,
			handleReset,
		}
	},

	components: {
		VaultsFilters,
		VaultCard,
		VaultCardLoading,
		Pagination,
		Breadcrumbs,
		Button,
	},
})
</script>

<template>
	<div :class="$style.wrapper">
		<Breadcrumbs :crumbs="breadcrumbs" :class="$style.breadcrumbs" />

		<Flex direction="column" gap="32">
			<Flex direction="column" gap="8">
				<h1>All Vaults</h1>
				<Text size="14" height="16" weight="500" color="tertiary">
					Explore and manage arbitrage strategies on Etherlink.
				</Text>
			</Flex>

			<Button
				@click="showFilters = !showFilters"
				type="secondary"
				size="small"
				block
				:class="$style.show_filters_btn"
			>
				<Icon name="filter" size="14" />
				{{ showFilters ? "Hide" : "Show" }} Filters
			</Button>

			<Flex gap="40" :class="$style.container">
				<VaultsFilters
					:filters="filters"
					:vaults="allVaults"
					:filtered-count="filteredVaults.length"
					@onSelect="handleSelect"
					@onReset="handleReset"
					:class="[$style.filters_block, showFilters && $style.show]"
				/>

				<div :class="$style.vaults_base">
					<div v-if="isLoading" :class="$style.grid">
						<VaultCardLoading v-for="i in 4" :key="i" />
					</div>

					<template v-else>
						<div v-if="filteredVaults.length" :class="$style.grid">
							<VaultCard
								v-for="vault in paginatedVaults"
								:key="vault.id"
								:vault="vault"
							/>
						</div>

						<div v-else :class="$style.empty">
							<Icon name="help" size="48" color="tertiary" />
							<Text size="16" weight="600" color="secondary">No vaults found</Text>
							<Text size="14" color="tertiary">Try adjusting your filters to see more results.</Text>
						</div>

						<Pagination
							v-if="filteredVaults.length > 4"
							v-model="currentPage"
							:total="filteredVaults.length"
							:limit="4"
							:class="$style.pagination"
						/>
					</template>
				</div>
			</Flex>
		</Flex>
	</div>
</template>

<style module>
.wrapper {
	max-width: 1250px;
}

.breadcrumbs {
	margin-bottom: 24px;
}

.container {
	display: flex;
}

.filters_block {
	width: 300px;
	flex-shrink: 0;
}

.vaults_base {
	flex: 1;
}

.grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
	gap: 24px;
}

.empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 80px 0;
	gap: 12px;
	text-align: center;
}

.show_filters_btn {
	display: none;
}

@media (max-width: 900px) {
	.container {
		flex-direction: column;
		gap: 24px;
	}

	.filters_block {
		width: 100%;
		display: none;
	}

	.filters_block.show {
		display: block;
	}

	.show_filters_btn {
		display: flex;
	}
}

.loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 100px 0;
	gap: 16px;
}

.pagination {
	margin-top: 24px;
	display: flex;
	justify-content: center;
}
</style>
