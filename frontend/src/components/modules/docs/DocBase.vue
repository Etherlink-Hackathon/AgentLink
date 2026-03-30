<script setup>
/**
 * Vendor
 */
import { onMounted, onBeforeUnmount, ref, watch, computed } from "vue"
import { DateTime } from "luxon"

/**
 * UI
 */
import Tooltip from "@ui/Tooltip.vue"

/**
 * Modules
 */
import ArticleContent from "./ArticleContent.vue"
import TableOfContents from "./TableOfContents.vue"

/**
 * Store
 */
import { useDocsStore } from "@store/docs"

const docsStore = useDocsStore()

const links = ref([])

onMounted(() => {
	document.addEventListener("keydown", onKeydown)

	if (!docsStore.post.content) return
	createLinksStructure()
})

onBeforeUnmount(() => {
	document.removeEventListener("keydown", onKeydown)
})

watch(
	() => docsStore.post,
	() => {
		createLinksStructure()
	},
)

const createLinksStructure = () => {
	if (!docsStore.post.markdown) {
		links.value = []
		return
	}

	const headerRegex = /^(#{1,6})\s+(.*)$/gm
	const foundLinks = []
	let match

	while ((match = headerRegex.exec(docsStore.post.markdown)) !== null) {
		foundLinks.push({
			level: match[1].length,
			text: match[2].trim(),
		})
	}

	links.value = foundLinks
}

/** Handle ArrowLeft / ArrowRight navigation */
const onKeydown = (e) => {
	if (e.key === "ArrowLeft") {
		handlePrevPage()
	}

	if (e.key === "ArrowRight") {
		handleNextPage()
	}
}

const nextPost = computed(() => {
	if (!docsStore.post.section) return

	const currentSection = docsStore.post.section.title
	const selectedPostIndex = docsStore.sections[currentSection].indexOf(
		docsStore.post,
	)

	if (docsStore.sections[currentSection][selectedPostIndex + 1]) {
		return docsStore.sections[currentSection][selectedPostIndex + 1]
	} else {
		const allSections = Object.keys(docsStore.sections)
		const currentSectionIndex = allSections.indexOf(currentSection)

		return (
			docsStore.sections[allSections[currentSectionIndex + 1]] &&
			docsStore.sections[allSections[currentSectionIndex + 1]][0]
		)
	}
})

const prevPost = computed(() => {
	if (!docsStore.post.section) return

	const currentSection = docsStore.post.section.title
	const selectedPostIndex = docsStore.sections[currentSection].indexOf(
		docsStore.post,
	)

	if (docsStore.sections[currentSection][selectedPostIndex - 1]) {
		return docsStore.sections[currentSection][selectedPostIndex - 1]
	} else {
		const allSections = Object.keys(docsStore.sections)
		const currentSectionIndex = allSections.indexOf(currentSection)
		const prevSection =
			docsStore.sections[allSections[currentSectionIndex - 1]]

		return prevSection && prevSection[prevSection.length - 1]
	}
})

const handleNextPage = () => {
	if (!nextPost.value) return

	docsStore.post = nextPost.value

	document.getElementById("app").scrollTo({
		top: 0,
		behavior: "smooth",
	})
}

const handlePrevPage = () => {
	if (!prevPost.value) return

	docsStore.post = prevPost.value

	document.getElementById("app").scrollTo({
		top: 0,
		behavior: "smooth",
	})
}
</script>

<template>
	<Flex :class="$style.wrapper">
		<div :class="$style.container">
			<div :class="$style.content">
				<ArticleContent
					:title="docsStore.post.title"
					:content="docsStore.post.content"
					:markdown="docsStore.post.markdown"
				/>

				<Flex align="center" justify="between" :class="$style.navigation">
					<router-link
						v-if="prevPost"
						:to="`/docs/${prevPost.slug.current}`"
						:class="$style.nav_btn"
					>
						<Icon name="arrow" size="16" :style="{ transform: 'rotate(90deg)' }" />
						<Flex direction="column" gap="4">
							<Text size="12" weight="600" color="tertiary">Previous</Text>
							<Text size="14" weight="600" color="primary">{{ prevPost.title }}</Text>
						</Flex>
					</router-link>
					<div v-else />

					<router-link
						v-if="nextPost"
						:to="`/docs/${nextPost.slug.current}`"
						:class="[$style.nav_btn, $style.next]"
					>
						<Flex direction="column" align="end" gap="4">
							<Text size="12" weight="600" color="tertiary">Next</Text>
							<Text size="14" weight="600" color="primary">{{ nextPost.title }}</Text>
						</Flex>
						<Icon name="arrow" size="16" :style="{ transform: 'rotate(-90deg)' }" />
					</router-link>
				</Flex>
			</div>

			<div :class="$style.toc_wrapper">
				<TableOfContents :links="links" />
			</div>
		</div>
	</Flex>
</template>

<style module>
.wrapper {
	display: flex;
	justify-content: center;
	width: 100%;
	padding: 60px 40px;
}

.container {
	display: flex;
	gap: 60px;
	width: 100%;
	max-width: 1200px;
}

.content {
	flex: 1;

	transition: all 0.2s ease;
}

.next_btn svg {
	transition: all 0.2s ease;
}

.next_btn:hover {
	border: 2px solid var(--border-highlight);
}

.next_btn:hover svg {
	fill: var(--text-primary);
}

@media (max-width: 900px) {
	.wrapper {
		flex-direction: column-reverse;
		gap: 32px;
	}
}
</style>
