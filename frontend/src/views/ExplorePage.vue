<script setup>
import { onMounted } from "vue"
import Page from "@base/Page.vue"
import Button from "@ui/Button.vue"
import { analytics } from "@sdk"

onMounted(() => {
	analytics.log("onPage", { name: "Explore" })
})
</script>

<template>
	<Page>
		<div :class="$style.wrapper">
			<div :class="$style.content">
				<h1 :class="$style.title">AgentLink</h1>
				<p :class="$style.description">
					The next generation of sovereign yield management. 
					Deploy capital into automated arbitrage strategies on Etherlink with institutional-grade security and transparency.
				</p>
				<Flex gap="16" justify="center">
					<router-link to="/vaults">
						<Button type="primary" size="large">
							<Icon name="compass" size="20" />
							Explore Vaults
						</Button>
					</router-link>
					<router-link to="/docs">
						<Button type="secondary" size="large">
							Documentation
						</Button>
					</router-link>
				</Flex>
			</div>
		</div>
	</Page>
</template>

<style module>
.wrapper {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 60vh;
	padding: 0 20px;
}

.content {
	text-align: center;
	max-width: 800px;
}

.title {
	font-size: 56px;
	margin-bottom: 24px;
	line-height: 1.1;
	font-weight: 700;
	background: linear-gradient(135deg, var(--text-primary) 0%, var(--brand) 100%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	background-clip: text;
}

.description {
	font-size: 20px;
	line-height: 1.6;
	color: var(--text-secondary);
	margin-bottom: 48px;
}

@media (max-width: 768px) {
	.title {
		font-size: 40px;
	}

	.description {
		font-size: 18px;
	}
}
</style>
