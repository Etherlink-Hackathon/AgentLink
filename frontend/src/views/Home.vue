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
					<router-link to="/vaults" :class="$style['cta-button']">
						<Icon name="compass" size="20" />
						Explore Vaults
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
	min-height: calc(100vh - 200px); /* Account for header and footer */
	padding: 0 20px;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-white);
  background: var(--brand);
  border-radius: 12px;
  text-decoration: none;
  transition: transform 0.2s ease, background 0.2s ease;
}

.cta-button:hover {
  transform: translateY(-2px);
  background: var(--btn-primary-bg-hover);
}

.cta-button:active {
  transform: translateY(0);
}


.content {
  text-align: center;
  max-width: 600px;
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
	line-height: 1.5;
	color: var(--text-secondary);
	margin-bottom: 40px;
}

@media (max-width: 768px) {
	.title {
		font-size: 40px;
	}

	.description {
		font-size: 18px;
	}

	.cta-button {
		padding: 14px 28px;
		font-size: 16px;
	}
}
</style>
