<script setup>
/**
 * Vendor
 */
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useMeta } from "vue-meta"

/**
 * UI
 */
import Button from "@ui/Button.vue"

/**
 * Store
 */
import { useAccountStore } from "@store/account"

const router = useRouter()
const accountStore = useAccountStore()

const showAnimation = ref("slide")

onMounted(async () => {
	// Analytics log
  console.log("Exploring AgentLink Sovereign Vault")
})

/** Meta */
useMeta({
	title: "Explore",
	description: "AgentLink Sovereign Vault - Institutional-grade arbitrage strategy management on Etherlink.",
})
</script>

<template>
	<transition :name="showAnimation">
		<div :class="$style.wrapper">
			<metainfo>
				<template #title="{ content }">{{ content }} • AgentLink</template>
			</metainfo>

			<div :class="$style.hero">
				<div :class="$style.hero_content">
					<Icon name="logo_symbol" size="64" viewBox="0 0 100 100" :class="$style.hero_logo" />
					<h1 :class="$style.title">Sovereign Vault</h1>
					<p :class="$style.subtitle">
						Institutional-grade arbitrage strategy management. 
						Secure, automated, and optimized for the Etherlink ecosystem.
					</p>
					
					<div :class="$style.actions">
						<Button @click="router.push('/vaults')" type="primary" size="large">
							Go to Vaults
						</Button>
						<Button @click="router.push('/docs')" type="secondary" size="large">
							Read Documentation
						</Button>
					</div>
				</div>
			</div>

			<div :class="$style.features">
				<div :class="$style.feature_card">
					<Icon name="zap" size="24" :class="$style.feature_icon" />
					<h3>High Frequency</h3>
					<p>Real-time cross-DEX arbitrage execution with minimal latency.</p>
				</div>
				
				<div :class="$style.feature_card">
					<Icon name="shield" size="24" :class="$style.feature_icon" />
					<h3>Non-Custodial</h3>
					<p>You maintain full control over your assets with sovereign vault technology.</p>
				</div>
				
				<div :class="$style.feature_card">
					<Icon name="bar_chart" size="24" :class="$style.feature_icon" />
					<h3>Advanced Analytics</h3>
					<p>Monitor your performance with high-fidelity charts and live logs.</p>
				</div>
			</div>

			<div :class="$style.banner">
				<div :class="$style.banner_content">
					<h2>Secure Arbitrage Agent</h2>
					<p>Our agent continuously monitors liquidity pools on Etherlink to identify and capture profitable arbitrage opportunities automatically.</p>
					<div :class="$style.banner_stats">
            <div :class="$style.stat">
              <span :class="$style.stat_value">42793</span>
              <span :class="$style.stat_label">Etherlink Mainnet</span>
            </div>
            <div :class="$style.stat">
              <span :class="$style.stat_value">100%</span>
              <span :class="$style.stat_label">Sovereign Control</span>
            </div>
          </div>
				</div>
			</div>
		</div>
	</transition>
</template>

<style module>
.wrapper {
	max-width: 1250px;
	margin: 0 auto;
	padding: 60px 32px;
}

.hero {
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
	margin-bottom: 80px;
}

.hero_content {
  max-width: 800px;
}

.hero_logo {
  margin-bottom: 24px;
  fill: var(--brand);
}

.title {
	font-size: 48px;
	font-weight: 800;
	margin-bottom: 16px;
	color: var(--text-primary);
  letter-spacing: -1px;
}

.subtitle {
	font-size: 20px;
	line-height: 1.6;
	color: var(--text-secondary);
	margin-bottom: 40px;
}

.actions {
	display: flex;
	justify-content: center;
	gap: 16px;
}

.features {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
	gap: 24px;
	margin-bottom: 80px;
}

.feature_card {
	background: var(--card-bg);
	border: 1px solid var(--border);
	border-radius: 12px;
	padding: 32px;
	transition: transform 0.2s ease, border-color 0.2s ease;
}

.feature_card:hover {
  transform: translateY(-4px);
  border-color: var(--border-highlight);
}

.feature_icon {
  fill: var(--brand);
  margin-bottom: 20px;
}

.feature_card h3 {
	margin-bottom: 12px;
}

.feature_card p {
	color: var(--text-tertiary);
	font-size: 14px;
	line-height: 1.5;
}

.banner {
	background: linear-gradient(135deg, var(--card-bg) 0%, #1f1d33 100%);
	border-radius: 16px;
	padding: 60px;
	border: 1px solid var(--border);
}

.banner_content h2 {
	font-size: 32px;
	margin-bottom: 16px;
}

.banner_content p {
	color: var(--text-secondary);
	max-width: 600px;
	margin-bottom: 40px;
	line-height: 1.6;
}

.banner_stats {
  display: flex;
  gap: 48px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat_value {
  font-size: 24px;
  font-weight: 700;
  color: var(--brand);
}

.stat_label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-support);
  text-transform: uppercase;
}

@media (max-width: 700px) {
  .title {
    font-size: 36px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .banner {
    padding: 40px 24px;
  }
  
  .banner_stats {
    flex-direction: column;
    gap: 24px;
  }
}
</style>
