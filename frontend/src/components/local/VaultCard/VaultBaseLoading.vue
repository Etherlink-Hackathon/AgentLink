<script setup>
import Flex from "@layout/Flex.vue"

</script>

<template>
	<div :class="$style.wrapper">

		<Flex direction="column" gap="32">
			<!-- Header Skeleton -->
			<Flex justify="between" align="center" wrap="wrap" gap="20">
				<Flex direction="column" gap="12">
					<div :class="[$style.skeleton, $style.title]" />
					<div :class="[$style.skeleton, $style.subtitle]" />
				</Flex>
				<Flex gap="12">
					<div :class="[$style.skeleton, $style.button]" />
					<div :class="[$style.skeleton, $style.button]" />
				</Flex>
			</Flex>

			<!-- Stats Row Skeleton -->
			<div :class="$style.stats_row">
				<div v-for="index in 4" :key="index" :class="$style.stat_block">
					<div :class="[$style.skeleton, $style.stat_label]" />
					<div :class="[$style.skeleton, $style.stat_value]" />
				</div>
			</div>

			<!-- Tabs Header Skeleton -->
			<div :class="$style.tabs_header">
				<div :class="[$style.skeleton, $style.tab]" />
				<div :class="[$style.skeleton, $style.tab]" />
			</div>

			<!-- Content Grid Skeleton -->
			<div :class="$style.grid">
				<div :class="$style.left">
					<Flex direction="column" gap="24">
						<!-- Chart Skeleton -->
						<div :class="$style.chart_card">
							<Flex justify="between" align="center" :class="$style.card_header">
								<div :class="[$style.skeleton, $style.card_title]" />
								<div :class="[$style.skeleton, $style.toggles]" />
							</Flex>
							<div :class="[$style.skeleton, $style.chart_placeholder]" />
						</div>

						<!-- Active Pools Skeleton -->
						<div :class="$style.card">
							<div :class="[$style.skeleton, $style.card_title]" />
							<div :class="$style.table_skeleton">
								<div v-for="i in 3" :key="i" :class="$style.table_row">
									<div :class="[$style.skeleton, $style.cell_lg]" />
									<div :class="[$style.skeleton, $style.cell_md]" />
									<div :class="[$style.skeleton, $style.cell_sm]" />
									<div :class="[$style.skeleton, $style.cell_sm]" />
								</div>
							</div>
						</div>
					</Flex>
				</div>

				<div :class="$style.right">
					<!-- Deposit Card Skeleton -->
					<div :class="$style.deposit_card">
						<div :class="[$style.skeleton, $style.deposit_tabs]" />
						<Flex direction="column" gap="12">
							<Flex justify="between">
								<div :class="[$style.skeleton, $style.label_sm]" />
								<div :class="[$style.skeleton, $style.label_sm]" />
							</Flex>
							<div :class="[$style.skeleton, $style.input]" />
							<Flex gap="8">
								<div v-for="i in 4" :key="i" :class="[$style.skeleton, $style.preset]" />
							</Flex>
						</Flex>
						<div :class="[$style.skeleton, $style.submit_btn]" />
					</div>
				</div>
			</div>
		</Flex>
	</div>
</template>

<style module>
.wrapper {
	max-width: 1250px;
}

.breadcrumbs {
	margin-bottom: 24px;
	opacity: 0.5;
}

@keyframes mig {
	0% {
		background: rgba(255, 255, 255, 0.05);
	}
	50% {
		background: rgba(255, 255, 255, 0.12);
	}
	100% {
		background: rgba(255, 255, 255, 0.05);
	}
}

.skeleton {
	animation: mig 2s infinite ease-in-out;
	border-radius: 4px;
	background: rgba(255, 255, 255, 0.05);
}

/* Header */
.title { height: 32px; width: 240px; }
.subtitle { height: 16px; width: 180px; }
.button { height: 36px; width: 120px; border-radius: 8px; }

/* Stats Row */
.stats_row {
	display: flex;
	align-items: center;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
	padding: 24px;
	gap: 40px;
}

.stat_block {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.stat_label { height: 12px; width: 80px; }
.stat_value { height: 28px; width: 100px; }

/* Tabs */
.tabs_header {
	display: flex;
	gap: 32px;
	border-bottom: 1px solid var(--border);
	padding-bottom: 12px;
}

.tab { height: 20px; width: 80px; }

/* Grid */
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

.chart_card {
	padding: 24px;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
}

.card_header { margin-bottom: 24px; }
.card_title { height: 18px; width: 120px; }
.toggles { height: 28px; width: 100px; border-radius: 6px; }
.chart_placeholder { height: 240px; width: 100%; border-radius: 8px; }

/* Table */
.table_skeleton { margin-top: 16px; }
.table_row {
	display: flex;
	justify-content: space-between;
	padding: 16px 0;
	border-top: 1px solid var(--border);
}

.cell_lg { height: 14px; width: 120px; }
.cell_md { height: 14px; width: 80px; }
.cell_sm { height: 14px; width: 60px; }

/* Deposit Card */
.deposit_card {
	padding: 28px;
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
	display: flex;
	flex-direction: column;
	gap: 24px;
}

.deposit_tabs { height: 40px; border-radius: 10px; }
.label_sm { height: 10px; width: 60px; }
.input { height: 48px; border-radius: 8px; }
.preset { height: 32px; flex: 1; border-radius: 6px; }
.submit_btn { height: 48px; border-radius: 4px 7px 7px 4px; }

@media (max-width: 1000px) {
	.grid { grid-template-columns: 1fr; }
	.right { order: -1; }
}

@media (max-width: 900px) {
	.stats_row { flex-direction: column; align-items: flex-start; gap: 24px; }
}
</style>
