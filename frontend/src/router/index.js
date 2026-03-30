import { createRouter, createWebHistory } from 'vue-router'

/**
 * Store
 */
import { useAppStore } from "@store/app"
import { useAccountStore } from "@store/account"

// Lazy-load routes
const Explore = () => import('../views/Home.vue')
const Vaults = () => import('../views/VaultsPage.vue')
const VaultPage = () => import('../views/VaultPage.vue')
const DocsBase = () => import('../components/modules/docs/DocsBase.vue')
const DocBase = () => import('../components/modules/docs/DocBase.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/explore'
  },
  {
    path: '/explore',
    name: 'Explore',
    component: Explore
  },
  {
    path: '/vaults',
    name: 'Vaults',
    component: Vaults
  },
  {
    path: '/vaults/:id',
    name: 'VaultPage',
    component: VaultPage,
    props: true
  },
  {
    path: '/docs',
    component: DocsBase,
    children: [
      {
        path: '',
        name: 'Docs',
        component: DocBase
      },
      {
        path: ':slug',
        name: 'Doc',
        component: DocBase
      }
    ]
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((target, prev, next) => {
  const appStore = useAppStore()

  if (prev.name) appStore.prevRoute = prev

  next()
})

export default router 