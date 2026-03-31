<script setup>
import { computed } from "vue"
import Modal from "@ui/Modal.vue"
import Flex from "@ui/Flex.vue"
import Icon from "@ui/Icon.vue"
import Text from "@ui/Text.vue"
import Button from "@ui/Button.vue"
import { useNotificationsStore } from "@store/notifications"

const props = defineProps({
	show: Boolean,
	title: String,
	config: [Object, String],
})

const emit = defineEmits(["onClose"])
const notificationsStore = useNotificationsStore()

const formattedConfig = computed(() => {
	if (!props.config) return "{}"
	try {
		return JSON.stringify(props.config, null, 2)
	} catch (e) {
		return String(props.config)
	}
})

const handleCopy = () => {
	navigator.clipboard.writeText(formattedConfig.value)
	notificationsStore.create({
		notification: {
			type: "success",
			title: "Config copied",
			description: "Strategy configuration copied to clipboard",
			autoDestroy: true,
		},
	})
}
</script>

<template>
	<Modal :show="show" width="500" closable @onClose="emit('onClose')">
		<Flex align="center" justify="between" :class="$style.head">
			<Flex align="center" gap="8">
				<Icon name="settings" size="16" color="secondary" />
				<Text size="14" weight="600" color="primary">{{ title || 'Configuration' }}</Text>
			</Flex>
		</Flex>

		<Flex direction="column" gap="24" :class="$style.base">
			<div :class="$style.code_wrapper">
				<pre :class="$style.code"><code>{{ formattedConfig }}</code></pre>
			</div>

			<Button @click="handleCopy" type="secondary" size="small" block>
				<Icon name="copy" size="14" :class="$style.copy_icon"/>
				Copy Configuration
			</Button>
		</Flex>
	</Modal>
</template>

<style module>
.head {
	height: 56px;
	padding: 0 20px;
	border-bottom: 1px solid var(--border);
}

.close_icon {
	cursor: pointer;
	transition: color 0.2s;
}

.close_icon:hover {
	color: var(--text-primary);
}

.base {
	padding: 24px 20px;
}

.code_wrapper {
	background: var(--surface-01);
	border: 1px solid var(--border);
	border-radius: 8px;
	padding: 16px;
	max-height: 400px;
	overflow-y: auto;
}

.code {
	margin: 0;
	font-family: 'JetBrains Mono', monospace;
	font-size: 13px;
	line-height: 1.6;
	color: var(--text-secondary);
	white-space: pre-wrap;
	word-break: break-all;
}

.copy_icon {
	cursor: pointer;
	transition: color 0.2s;
}

.copy_icon:hover {
	color: var(--text-primary);
}
</style>
