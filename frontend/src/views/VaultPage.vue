<script setup>
import Page from "@base/Page.vue"
import VaultBase from "@modules/vault/VaultBase.vue"

const props = defineProps({
	id: {
		type: String,
		required: true,
	},
})
</script>

<template>
	<Page>
		<VaultBase :id="id" />
	</Page>
</template>

<style module>
.wrapper {
	max-width: 1250px;
}
</style>
