<script setup>
/**
 * Vendor
 */
import { computed, onMounted, watch, nextTick } from "vue"
import MarkdownIt from "markdown-it"

const props = defineProps({
	title: String,
	content: Array,
	markdown: String,
})

const md = new MarkdownIt({
	html: true,
	linkify: true,
	typography: true,
})

// Custom rendering for mermaid code blocks
const defaultFence = md.renderer.rules.fence
md.renderer.rules.fence = (tokens, idx, options, env, slf) => {
	const token = tokens[idx]
	if (token.info.trim() === "mermaid") {
		return `<div class="mermaid">${token.content}</div>`
	}
	return defaultFence(tokens, idx, options, env, slf)
}

const renderedHtml = computed(() => {
	if (props.markdown) {
		return md.render(props.markdown)
	}
	return ""
})

const renderMermaid = async () => {
	if (window.mermaid) {
		try {
			await window.mermaid.run({
				querySelector: ".mermaid",
			})
		} catch (e) {
			console.error("Mermaid render error:", e)
		}
	}
}

onMounted(() => {
	if (window.mermaid) {
		window.mermaid.initialize({
			startOnLoad: false,
			theme: "dark",
			securityLevel: "loose",
			themeVariables: {
				primaryColor: "#00f2ff",
				primaryTextColor: "#fff",
				primaryBorderColor: "#00f2ff",
				lineColor: "#00f2ff",
				secondaryColor: "#00b8d4",
				tertiaryColor: "#1a1a1c",
			},
		})
		renderMermaid()
	}
})

watch(
	() => props.markdown,
	() => {
		nextTick(() => {
			renderMermaid()
		})
	},
)
</script>

<template>
	<div :class="$style.wrapper">
		<h1 v-if="title">{{ title }}</h1>
		<div v-if="markdown" v-html="renderedHtml" :class="$style.markdown_content" />
	</div>
</template>

<style module>
.wrapper {
}

.wrapper h1 {
	margin: 0 0 1em 0;
}

.markdown_content :global(h1) { margin: 1.5em 0 1em 0; font-size: 28px; font-weight: 700; color: var(--text-primary); }
.markdown_content :global(h2) { 
	margin: 2.5em 0 1.2em 0; 
	font-size: 22px; 
	font-weight: 600; 
	color: var(--text-primary); 
	border-bottom: 1px solid var(--border); 
	padding-bottom: 12px; 
}
.markdown_content :global(h3) { margin: 2em 0 1em 0; font-size: 18px; font-weight: 600; color: var(--text-primary); }

.markdown_content :global(p) { 
	font-size: 15px; 
	line-height: 1.7; 
	color: var(--text-secondary); 
	margin: 1.2em 0; 
}

.markdown_content :global(ul), .markdown_content :global(ol) {
	margin: 1.5em 0;
	padding-left: 1.5em;
	color: var(--text-secondary);
}

.markdown_content :global(li) {
	margin: 0.8em 0;
	font-size: 15px;
	line-height: 1.6;
}

.markdown_content :global(code) {
	background: var(--opacity-05);
	padding: 3px 6px;
	border-radius: 4px;
	font-family: 'JetBrains Mono', monospace;
	font-size: 13px;
	color: var(--brand);
}

.markdown_content :global(pre) {
	background: #0d0d0f;
	padding: 20px;
	border-radius: 12px;
	overflow: auto;
	margin: 2em 0;
	border: 1px solid var(--border);
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.markdown_content :global(pre code) {
	background: transparent;
	padding: 0;
	color: #e2e2e2;
	font-size: 13px;
	line-height: 1.6;
}

.markdown_content :global(a) {
	color: var(--brand);
	font-weight: 500;
	text-decoration: none;
	border-bottom: 1px solid transparent;
	transition: all 0.2s ease;
}

.markdown_content :global(a:hover) {
	border-bottom-color: var(--brand);
}

.markdown_content :global(blockquote) {
	background: var(--opacity-03);
	border-left: 4px solid var(--brand);
	padding: 16px 24px;
	margin: 2.5em 0;
	border-radius: 0 8px 8px 0;
}

.markdown_content :global(blockquote p) {
	margin: 0;
	font-style: italic;
	color: var(--text-tertiary);
}

/* Tables */
.markdown_content :global(table) {
	width: 100%;
	border-collapse: separate;
	border-spacing: 0;
	margin: 2.5em 0;
	border: 1px solid var(--border);
	border-radius: 8px;
	overflow: hidden;
}

.markdown_content :global(th) {
	background: var(--opacity-05);
	text-align: left;
	padding: 12px 16px;
	font-size: 13px;
	font-weight: 600;
	color: var(--text-primary);
	border-bottom: 1px solid var(--border);
}

.markdown_content :global(td) {
	padding: 12px 16px;
	font-size: 14px;
	color: var(--text-secondary);
	border-bottom: 1px solid var(--border);
}

.markdown_content :global(tr:last-child td) {
	border-bottom: none;
}

.markdown_content :global(tr:nth-child(even)) {
	background: rgba(255, 255, 255, 0.01);
}

.markdown_content :global(strong) {
	color: var(--text-primary);
	font-weight: 600;
}

.markdown_content :global(img) {
	max-width: 100%;
	border-radius: 8px;
	margin: 2em 0;
}

.markdown_content :global(.mermaid) {
	display: flex;
	justify-content: center;
	padding: 32px;
	background: #0d0d0f;
	border-radius: 16px;
	margin: 3em 0;
	border: 1px solid var(--border);
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.markdown_content :global(.mermaid svg) {
	max-width: 100%;
	height: auto;
}

/* Ensure mermaid text is readable */
.markdown_content :global(.mermaid .nodeText),
.markdown_content :global(.mermaid .label) {
	font-family: 'Inter', sans-serif !important;
}
</style>
