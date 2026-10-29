import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: { name: 'dashboard' } },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('@/views/AuthView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'build-profile',
      component: () => import('@/views/BuildProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/matching',
      name: 'skill-matching',
      component: () => import('@/views/SkillMatchingView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/requests',
      name: 'swap-requests',
      component: () => import('@/views/SwapRequestsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/chat/:matchId?',
      name: 'chat-room',
      component: () => import('@/views/ChatRoomView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/progress',
      name: 'progress-tracking',
      component: () => import('@/views/ProgressTrackingView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'auth' }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
