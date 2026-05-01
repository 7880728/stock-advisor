import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
    { path: '/stock/:code', name: 'stock', component: () => import('../views/StockDetail.vue') },
    { path: '/strategy', name: 'strategy', component: () => import('../views/StrategyConfig.vue') },
    { path: '/signals', name: 'signals', component: () => import('../views/Signals.vue') },
  ],
})

export default router
