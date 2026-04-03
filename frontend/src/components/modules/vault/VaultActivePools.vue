<script>
import { defineComponent, ref, computed } from "vue"

/**
 * UI
 */
import Pagination from "@ui/Pagination.vue"

/**
 * Utils
 */
import { getTokenLogo, getDexIcon } from "@utils/misc"

export default defineComponent({
	name: "VaultActivePools",

	props: {
		pools: {
			type: Array,
			default: () => [],
		},
	},

	setup(props) {
		const currentPage = ref(1)
		const itemsPerPage = 5

		const paginatedPools = computed(() => {
			const start = (currentPage.value - 1) * itemsPerPage
			const end = start + itemsPerPage
			return props.pools.slice(start, end)
		})

		const getPairTokens = (vault) => {
			if (!vault) return []
			return vault.split("/")
		}

		return {
			currentPage,
			itemsPerPage,
			paginatedPools,
			getPairTokens,
			getTokenLogo,
			getDexIcon,
		}
	},

	components: {
		Pagination,
	},
})

</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.table_container">
			<table :class="$style.table">
				<thead>
					<tr>
						<th>DEX</th>
						<th>POOL</th>
						<th>ALLOCATION</th>
						<th :class="$style.align_right">LIQUIDITY</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(pool, index) in paginatedPools" :key="index">
						<td>
							<Flex align="center" gap="10">
								<div :class="$style.pool_icon_wrapper">
									<img v-if="pool.dexPools" :src="getDexIcon(pool.dexPools.name)" :class="$style.pool_icon_img" />
									<div v-else :class="$style.pool_icon_placeholder" />
								</div>
								<Text size="13" weight="600" color="secondary">{{ pool.dexPools?.name || 'Unknown' }}</Text>
							</Flex>
						</td>
						<td>
							<Flex align="center" gap="8">
								<div :class="$style.token_icons">
									<img 
										v-if="pool.dexPools?.tokenA?.symbol"
										:src="getTokenLogo(pool.dexPools.tokenA.symbol)"
										:class="$style.token_icon"
									/>
									<img 
										v-if="pool.dexPools?.tokenB?.symbol"
										:src="getTokenLogo(pool.dexPools.tokenB.symbol)"
										:class="$style.token_icon"
									/>
								</div>
								<Text size="13" weight="600" color="primary">
									{{ pool.dexPools?.tokenA?.symbol || '?' }}/{{ pool.dexPools?.tokenB?.symbol || '?' }}
								</Text>
							</Flex>
						</td>
						<td>
							<Text size="13" weight="600" color="green">{{ pool.allocation || '—' }}</Text>
						</td>
						<td>
							<Text size="13" weight="600" color="secondary">{{ pool.liquidity || '—' }}</Text>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<Pagination
			v-if="pools.length > itemsPerPage"
			v-model="currentPage"
			:total="pools.length"
			:limit="itemsPerPage"
			:class="$style.pagination"
		/>
	</div>
</template>

<style module>
.wrapper {
	padding: 24px;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
}

.title {
	margin-bottom: 24px;
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
	padding: 12px 0;
	letter-spacing: 0.05em;
	text-transform: uppercase;
}

.table td {
	padding: 16px 0;
	border-top: 1px solid var(--border);
}

.pool_icon_wrapper {
	width: 24px;
	height: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.05);
	border-radius: 6px;
	overflow: hidden;
}

.pool_icon_img {
	width: 18px;
	height: 18px;
	object-fit: contain;
}

.pool_icon_placeholder {
	width: 16px;
	height: 16px;
	background: var(--border);
	border-radius: 4px;
}

.token_icons {
	display: flex;
	align-items: center;
}

.token_icon {
	width: 22px;
	height: 22px;
	border-radius: 50%;
	border: 2px solid var(--card-bg);
	background: var(--surface-01);
	position: relative;
}

.token_icon:first-child {
	z-index: 2;
}

.token_icon:not(:first-child) {
	margin-left: -10px;
	z-index: 1;
}

.token_placeholder {
	background: var(--border);
	display: flex;
	align-items: center;
	justify-content: center;
}

.align_right {
	text-align: right;
}

.pagination {
	margin-top: 24px;
	display: flex;
	justify-content: center;
}
</style>
