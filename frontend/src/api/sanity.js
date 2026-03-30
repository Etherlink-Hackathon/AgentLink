import overviewRaw from "../../../docs/OVERVIEW.md?raw"
import agentRaw from "../../../docs/AGENT.md?raw"
import dexPoolsRaw from "../../../docs/DEX_POOLS.md?raw"
import securityRaw from "../../../docs/SECURITY.md?raw"
import riskRaw from "../../../docs/RISK.md?raw"
import contractsRaw from "../../../docs/DEPLOYED_CONTRACTS.md?raw"
import lpVaultRaw from "../../../docs/LP_VAULT.md?raw"

export const fetchPosts = async () => {
	return [
		{
			_id: "overview",
			title: "Project Overview",
			slug: { current: "overview" },
			icon: "package",
			markdown: overviewRaw,
			content: [],
		},
		{
			_id: "agent",
			title: "Agent Architecture",
			slug: { current: "agent" },
			section: { title: "Architecture" },
			markdown: agentRaw,
			content: [],
		},
		{
			_id: "lp-vault",
			title: "Overview",
			slug: { current: "lp-vault" },
			section: { title: "LP Vault" },
			markdown: lpVaultRaw,
			content: [],
		},
		{
			_id: "security",
			title: "Security & Trust",
			slug: { current: "security" },
			section: { title: "Architecture" },
			markdown: securityRaw,
			content: [],
		},
		{
			_id: "risk",
			title: "Risk Disclosure",
			slug: { current: "risk" },
			section: { title: "Architecture" },
			markdown: riskRaw,
			content: [],
		},
		{
			_id: "dex-pools",
			title: "Available DEX Pools",
			slug: { current: "dex-pools" },
			section: { title: "Infrastructure" },
			markdown: dexPoolsRaw,
			content: [],
		},
		{
			_id: "deployed-contracts",
			title: "Deployed Contracts",
			slug: { current: "deployed-contracts" },
			section: { title: "Infrastructure" },
			markdown: contractsRaw,
			content: [],
		},
	]
}

export const fetchPostById = async (id) => {
	const posts = await fetchPosts()
	return posts.find((p) => p._id === id) || {}
}

export const fetchSections = async () => {
	return [
		{ _id: "sec1", title: "Architecture" },
		{ _id: "sec2", title: "Infrastructure" },
		{ _id: "sec3", title: "LP Vault" },
	]
}

// Stubs for other functions to prevent crashes
export const fetchArticles = async () => []
export const fetchArticleBySlug = async () => ({})
export const fetchReleases = async () => []