<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/authStore'
import { useChatStore } from '@/stores/chatStore'
import { useMatchStore } from '@/stores/matchStore'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const matchStore = useMatchStore()
const chatStore = useChatStore()
const { isDarkMode, toggleTheme } = useTheme()

const navItems = computed(() => [
  { label: 'Dashboard', icon: 'grid', to: { name: 'dashboard' } },
  { label: 'Build Profile', icon: 'user', to: { name: 'build-profile' } },
  { label: 'Skill Matching', icon: 'swap', to: { name: 'skill-matching' } },
  { label: 'Swap Requests', icon: 'inbox', to: { name: 'swap-requests' }, count: matchStore.incomingCount },
  { label: 'Chat Room', icon: 'chat', to: { name: 'chat-room' }, count: chatStore.totalUnread },
  { label: 'AI Interview', icon: 'gear' },
  { label: 'Progress Tracking', icon: 'chart', to: { name: 'progress-tracking' } },
])

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] ?? 'there')
const userInitial = computed(() => (auth.user?.full_name ?? 'U').trim().charAt(0).toUpperCase())

let inboxTimer = null

function pollInbox() {
  matchStore.refresh()
  chatStore.refresh()
}

onMounted(() => {
  if (!auth.user) {
    auth.loadProfile().catch(() => auth.logout())
  }
  if (!matchStore.loadedOnce) {
    matchStore.loadInbox()
  }
  if (!chatStore.loadedOnce) {
    chatStore.load()
  }
  inboxTimer = setInterval(pollInbox, 15000)
  document.addEventListener('visibilitychange', pollInbox)
})

onUnmounted(() => {
  clearInterval(inboxTimer)
  document.removeEventListener('visibilitychange', pollInbox)
})

watch(() => route.name, pollInbox)

function handleLogout() {
  auth.logout()
  matchStore.reset()
  chatStore.reset()
  router.push({ name: 'auth' })
}
</script>

<template>
  <div class="flex min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)]">
    <!-- Sidebar -->
    <aside class="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-[var(--border-color)] bg-[var(--bg-surface)] p-4 lg:flex">
      <RouterLink :to="{ name: 'dashboard' }" class="mb-8 flex items-center gap-2.5 px-2 pt-1">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--accent-primary)] text-lg font-bold text-white">⇄</div>
        <span class="text-lg font-bold">Skill Swap</span>
      </RouterLink>

      <nav class="flex-1 space-y-1">
        <component
          :is="item.to ? 'RouterLink' : 'button'"
          v-for="item in navItems"
          :key="item.label"
          :to="item.to"
          type="button"
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
          :class="item.to && item.to.name === route.name
            ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]'
            : 'text-[var(--text-secondary)] hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]'"
        >
          <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <template v-if="item.icon === 'grid'"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></template>
            <template v-else-if="item.icon === 'user'"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></template>
            <template v-else-if="item.icon === 'swap'"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></template>
            <template v-else-if="item.icon === 'inbox'"><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></template>
            <template v-else-if="item.icon === 'chat'"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></template>
            <template v-else-if="item.icon === 'gear'"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></template>
            <template v-else><path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/></template>
          </svg>
          <span class="flex-1 text-left">{{ item.label }}</span>
          <span
            v-if="item.count"
            class="min-w-5 rounded-full px-1.5 py-0.5 text-center text-[10px] font-bold leading-5"
            :class="item.to.name === route.name
              ? 'bg-[var(--accent-primary)] text-white'
              : 'bg-[var(--bg-base)] text-[var(--text-secondary)]'"
          >{{ item.count }}</span>
        </component>
      </nav>

      <div class="space-y-1 border-t border-[var(--border-color)] pt-4">
        <button type="button" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="9"/></svg>
          Account
        </button>
        <button type="button" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-red-500" @click="handleLogout">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></svg>
          Log out
        </button>
      </div>
    </aside>

    <!-- Main column -->
    <div class="flex min-w-0 flex-1 flex-col">
      <header class="border-b border-[var(--border-color)] bg-[var(--bg-surface)] px-5 py-4 lg:px-8">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 class="text-xl font-bold lg:text-2xl">Hello, {{ firstName }}! Let's swap skills today</h1>
            <slot name="header-sub">
              <p class="mt-1 text-xs text-[var(--text-secondary)]">
                Swap Hrs: <span class="font-semibold text-[var(--text-primary)]">24</span>
                <span class="mx-2 opacity-40">|</span>
                Skill Twins: <span class="font-semibold text-[var(--text-primary)]">5</span>
              </p>
            </slot>
          </div>

          <div class="flex items-center gap-3">
            <div class="relative hidden md:block">
              <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              <input
                type="search"
                placeholder="Search..."
                class="w-48 rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] py-2 pl-9 pr-3 text-sm outline-none transition focus:border-[var(--accent-primary)] xl:w-64"
              />
            </div>

            <RouterLink
              :to="{ name: 'swap-requests' }"
              type="button"
              title="Swap Requests"
              class="relative rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] p-2 text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]"
            >
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
              <span
                v-if="matchStore.incomingCount"
                class="absolute -right-1 -top-1 min-w-4 rounded-full bg-[var(--accent-primary)] px-1 text-center text-[10px] font-bold leading-4 text-white ring-2 ring-[var(--bg-surface)]"
              >{{ matchStore.incomingCount }}</span>
              <span v-else class="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-[var(--border-color)] ring-2 ring-[var(--bg-surface)]"></span>
            </RouterLink>

            <div class="flex items-center gap-2">
              <img v-if="auth.user?.avatar" :src="auth.user.avatar" alt="Your avatar" class="h-9 w-9 shrink-0 rounded-full object-cover" />
              <div v-else class="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--accent-primary)] text-sm font-bold text-white">{{ userInitial }}</div>
              <span class="hidden text-sm font-semibold sm:block">Hello, {{ firstName }}!</span>
              <svg class="h-4 w-4 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m6 9 6 6 6-6"/></svg>
            </div>
          </div>

          <!-- Theme toggle -->
          <div class="flex w-full justify-end">
            <div class="flex rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] p-1">
              <button type="button" class="rounded-md px-3 py-1 text-xs font-semibold transition" :class="!isDarkMode ? 'bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm' : 'text-[var(--text-secondary)]'" @click="toggleTheme(false)">☀ Light</button>
              <button type="button" class="rounded-md px-3 py-1 text-xs font-semibold transition" :class="isDarkMode ? 'bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm' : 'text-[var(--text-secondary)]'" @click="toggleTheme(true)">☾ Dark</button>
            </div>
          </div>
        </div>
      </header>

      <nav class="flex gap-1 overflow-x-auto border-b border-[var(--border-color)] bg-[var(--bg-surface)] px-3 py-2 lg:hidden">
        <RouterLink
          v-for="item in navItems.filter((entry) => entry.to)"
          :key="item.label"
          :to="item.to"
          class="flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition"
          :class="item.to.name === route.name
            ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]'
            : 'text-[var(--text-secondary)] hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]'"
        >
          {{ item.label }}
          <span
            v-if="item.count"
            class="rounded-full bg-[var(--accent-primary)] px-1.5 py-0.5 text-[10px] font-bold leading-none text-white"
          >{{ item.count }}</span>
        </RouterLink>
      </nav>

      <main class="flex-1 p-5 lg:px-8">
        <slot />
      </main>
    </div>
  </div>
</template>
