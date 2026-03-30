<script setup>
import { ref, onBeforeMount } from "vue"

const props = defineProps({
	code: Object,
	title: String,
})

const result = ref("")

onBeforeMount(() => {
	const { code } = props.code
	result.value = `<pre><code>${code}</code></pre>`
})
</script>

<template>
	<Flex direction="column" align="center" gap="8" :class="$style.wrapper">
		<div v-html="result" :class="$style.code" />

		<Text size="12" color="tertiary" weight="500" :class="$style.lang">
			{{ code.language }}
		</Text>

		<Text v-if="title" size="12" color="support" weight="500">
			{{ title }}
		</Text>
	</Flex>
</template>

<style module>
.wrapper {
	position: relative;

	margin-bottom: 40px;
}

.code {
	width: 100%;

	border-radius: 8px;
	overflow: auto;
}

.code pre {
	background-color: rgba(0, 0, 0, 0.2) !important;

	font-size: 14px;

	padding: 16px;
}

.lang {
	position: absolute;
	top: 16px;
	right: 16px;

	user-select: none;
}
</style>
