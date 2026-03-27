/* eslint-disable vue/multi-word-component-names */
import { createApp, h } from "vue"
import { createMetaManager } from "vue-meta"
import { createPinia } from "pinia"
import { useAccountStore } from './store/account';

// Import modules.
import { VueQueryPlugin } from '@tanstack/vue-query';
import { WagmiPlugin } from '@wagmi/vue';
import { config } from '@config';

/** Analytics */
import VueGtag from "vue-gtag"
// import amplitude from "amplitude-js"
// amplitude.getInstance().init(import.meta.env.VITE_AMPLITUDE)

// import "@sdk"


import App from "./App.vue"
import router from "./router"

// Create app
const app = createApp({
	render: () => h(App),
})

/**
 * Use plugins
 */
app.use(router)
app.use(createPinia())
app.use(createMetaManager())
app.use(VueGtag, { config: { id: "G-58LD5WNLR4" } })
// Add Wagmi and Vue Query plugins
app.use(WagmiPlugin, { config })
app.use(VueQueryPlugin, {})

/**
 * Provide
 */
// app.provide("amplitude", amplitude.getInstance())

/**
 * Global components
 */
import Icon from "@/components/icons/Icon.vue"
import Flex from "@layout/Flex.vue"
import Text from "@typography/Text.vue"
app.component("Icon", Icon)
app.component("Flex", Flex)
app.component("Text", Text)

/**
 * Initialize wallet connection
 */
const accountStore = useAccountStore();
// Initialize wallet after Wagmi is set up
app.mount("#app")
// Initialize wallet after the app is mounted
accountStore.init();
