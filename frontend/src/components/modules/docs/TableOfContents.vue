<script setup>
/**
 * Vendor
 */
import { ref } from "vue"

const props = defineProps({
	title: { type: String, default: "AgentLink Documentation" },
	links: Array,
})

const expand = ref(false)

const generateHref = (text) => {
	return text
		.toString()
		.toLowerCase()
		.replace(/\s+/g, "-")
		.replace(/[^\w\-]+/g, "")
		.replace(/\-\-+/g, "-")
		.replace(/^-+/, "")
		.replace(/-+$/, "")
}
</script>

<template>
	<div :class="$style.wrapper">
		<div :class="$style.base">
			<div @click="expand = !expand" :class="$style.label">
				<Flex align="center" gap="6">
					Content

					<Icon
						name="arrow"
						size="14"
						color="tertiary"
						:style="{ transform: `rotate(${expand ? 180 : 0}deg)` }"
						:class="$style.mobile_arrow"
					/>
				</Flex>
			</div>

			<div :class="[$style.content, $style.mobile, expand && $style.expand]">
				<Text size="14" weight="600" color="primary">
					{{ title }}
				</Text>

				<ul>
					<li v-for="link in links" :style="{ paddingLeft: `${(link.level - 2) * 10}px` }">
						<a :href="`#${generateHref(link.text)}`">{{ link.text }}</a>
					</li>
				</ul>
			</div>
		</div>
	</div>
</template>

<style module>
.wrapper {
	position: relative;
	width: 100%;
}

.base {
	display: flex;
	flex-direction: column;
	gap: 20px;

	position: sticky;
	top: 130px;
}

.label {
	font-size: 11px;
	font-weight: 700;
	color: var(--text-tertiary);
	text-transform: uppercase;
	letter-spacing: 0.1em;
	margin-bottom: 8px;
}

.wrapper ul {
	display: flex;
	flex-direction: column;

	padding-inline-start: 0px;
	list-style-type: none;

	margin: 0;
}

.wrapper li {
	display: block;
	overflow: hidden;
	text-overflow: ellipsis;
}

.wrapper li a {
	display: flex;
	padding: 6px 0;
	font-size: 13px;
	line-height: 1.4;
	font-weight: 500;
	color: var(--text-secondary);
	text-decoration: none;
	transition: all 0.2s ease;
	white-space: normal;
}

.wrapper li a:hover {
	color: var(--brand);
	transform: translateX(4px);
}

.mobile_arrow {
	display: none;
}

@media (max-width: 900px) {
	.wrapper {
		padding-left: 0;
	}
}

@media (max-width: 600px) {
	.mobile {
		display: none;
	}

	.expand {
		display: initial;
	}

	.mobile_arrow {
		display: initial;
	}
}
</style>
