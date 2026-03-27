<script setup>
import { getTokenLogo } from "@utils/misc"

const props = defineProps({
	pools: {
		type: Array,
		default: () => []
	}
})

const getDexLogo = (dex) => {
	const name = dex.toLowerCase().replace(/[\s-]/g, '')
	if (name.includes('curve')) return new URL('../../../assets/img/curve.png', import.meta.url).href
	if (name.includes('oku')) return new URL('../../../assets/img/oku.svg', import.meta.url).href
	return null
}

const getPairTokens = (vault) => {
	if (!vault) return []
	return vault.split('/')
}
</script>

<template>
	<div :class="$style.wrapper">
		<Text size="14" weight="600" color="primary" :class="$style.title">Active DEX Pools</Text>
		
		<div :class="$style.table_container">
			<table :class="$style.table">
				<thead>
					<tr>
						<th>DEX</th>
						<th>VAULT</th>
						<th>ALLOCATION</th>
						<th :class="$style.align_right">LIQUIDITY</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(pool, index) in pools" :key="index">
						<td>
							<Flex align="center" gap="10">
								<div :class="$style.pool_icon_wrapper">
									<img v-if="getDexLogo(pool.dex)" :src="getDexLogo(pool.dex)" :class="$style.pool_icon_img" />
									<div v-else :class="$style.pool_icon_placeholder" />
								</div>
								<Text size="13" weight="600" color="secondary">{{ pool.dex }}</Text>
							</Flex>
						</td>
						<td>
							<Flex align="center" gap="8">
								<div :class="$style.token_icons">
									<template v-for="token in getPairTokens(pool.vault)" :key="token">
										<img 
											v-if="getTokenLogo(token)"
											:src="getTokenLogo(token)"
											:class="$style.token_icon"
										/>
										<div v-else :class="[$style.token_icon, $style.token_placeholder]" />
									</template>
								</div>
								<Text size="13" weight="600" color="primary">{{ pool.vault }}</Text>
							</Flex>
						</td>
						<td>
							<Text size="13" weight="600" color="green">{{ pool.allocation }}</Text>
						</td>
						<td :class="$style.align_right">
							<Text size="13" weight="600" color="secondary">{{ pool.liquidity }}</Text>
						</td>
					</tr>
				</tbody>
			</table>
		</div>
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
</style>
