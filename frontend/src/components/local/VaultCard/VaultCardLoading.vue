<script setup>
/**
 * UI Components
 */
import Flex from "@layout/Flex.vue"
</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.header">
			<div :class="$style.symbol_imgs">
				<div :class="$style.skeleton" />
				<div :class="$style.skeleton" />
			</div>

			<div :class="$style.users">
				<div :class="[$style.skeleton, $style.avatar]" />
				<div :class="[$style.skeleton, $style.avatar]" />
				<div :class="[$style.skeleton, $style.avatar]" />
			</div>
		</div>

		<div :class="[$style.skeleton, $style.title]" />

		<div :class="$style.description">
			<div :class="[$style.skeleton, $style.icon]" />
			<div :class="[$style.skeleton, $style.text_sm]" />
			<div :class="$style.dot" />
			<div :class="[$style.skeleton, $style.text_xs]" />
		</div>

		<div :class="$style.badges">
			<div :class="[$style.skeleton, $style.badge_lg]" />
			<div :class="[$style.skeleton, $style.badge_md]" />
		</div>

		<div :class="$style.footer">
			<div :class="$style.footer_item">
				<div :class="[$style.skeleton, $style.label]" />
				<div :class="[$style.skeleton, $style.value]" />
			</div>
			<div :class="$style.footer_item">
				<div :class="[$style.skeleton, $style.label]" />
				<div :class="[$style.skeleton, $style.value]" />
			</div>
			<div :class="$style.footer_item_end">
				<div :class="[$style.skeleton, $style.label]" />
				<div :class="[$style.skeleton, $style.value]" />
			</div>
		</div>
	</div>
</template>

<style module>
.wrapper {
	background: var(--card-bg);
	border-radius: 8px;
	padding: 20px;
	border: 1px solid transparent;
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
}

.header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20px;
}

.symbol_imgs {
	position: relative;
	width: 34px;
	height: 34px;
}

.symbol_imgs div {
	width: 22px;
	height: 22px;
	border-radius: 5px;
}

.symbol_imgs div:first-child {
	position: absolute;
	z-index: 1;
	outline: 3px solid var(--card-bg);
}

.symbol_imgs div:last-child {
	position: absolute;
	bottom: 0;
	right: 0;
}

.users {
	display: flex;
	align-items: center;
}

.avatar {
	width: 30px;
	height: 30px;
	border-radius: 50% !important;
	border: 3px solid var(--card-bg);
	margin-left: -10px;
}

.title {
	width: 60%;
	height: 18px;
	margin-bottom: 12px;
}

.description {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 24px;
}

.icon {
	width: 12px;
	height: 12px;
}

.text_sm {
	width: 80px;
	height: 10px;
}

.text_xs {
	width: 50px;
	height: 10px;
}

.dot {
	width: 4px;
	height: 4px;
	border-radius: 50%;
	background: var(--opacity-10);
}

.badges {
	display: flex;
	gap: 8px;
	margin-bottom: 24px;
}

.badge_lg {
	width: 80px;
	height: 24px;
	border-radius: 50px !important;
}

.badge_md {
	width: 70px;
	height: 24px;
	border-radius: 50px !important;
}

.footer {
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
	padding-top: 16px;
	border-top: 1px solid var(--border);
}

.footer_item {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.footer_item_end {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 6px;
}

.label {
	width: 30px;
	height: 8px;
}

.value {
	width: 50px;
	height: 16px;
}
</style>
