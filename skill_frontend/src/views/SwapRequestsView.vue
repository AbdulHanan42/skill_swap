<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppLayout from '@/components/common/AppLayout.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ToastMessage from '@/components/common/ToastMessage.vue'
import SwapRequestCard from '@/components/requests/SwapRequestCard.vue'
import SwapRequestSkeleton from '@/components/requests/SwapRequestSkeleton.vue'
import SwapTabs from '@/components/requests/SwapTabs.vue'
import { useMatchStore } from '@/stores/matchStore'

const router = useRouter()
const matchStore = useMatchStore()

const activeTab = ref('received')
const toast = ref('')
const toastType = ref('success')
let redirectTimer = null

const tabs = computed(() => [
  { key: 'received', label: 'Received Requests', count: matchStore.incomingCount },
  { key: 'sent', label: 'Sent Requests', count: matchStore.sentCount },
])

const rows = computed(() =>
  activeTab.value === 'received' ? matchStore.incoming : matchStore.sent,
)

const loading = computed(() => matchStore.loadingInbox && !matchStore.loadedOnce)

const headerSub = computed(() => {
  if (matchStore.loadingInbox && !matchStore.loadedOnce) return 'Loading your inbox…'
  const pending = matchStore.incomingCount
  return pending
    ? `${pending} pending swap ${pending === 1 ? 'request' : 'requests'} · ${matchStore.sentCount} sent`
    : `No pending requests · ${matchStore.sentCount} sent`
})

function notify(message, type = 'success') {
  toast.value = message
  toastType.value = type
}

async function accept(request) {
  const result = await matchStore.respond(request.match_id, 'accept')
  if (!result.ok) {
    if (!result.duplicate) notify(result.message, 'error')
    return
  }
  notify('Accepted! Opening chat room...')
  redirectTimer = setTimeout(() => {
    router.push({ name: 'chat-room', params: { matchId: String(request.match_id) } })
  }, 1500)
}

async function decline(request) {
  const result = await matchStore.respond(request.match_id, 'decline')
  if (!result.ok) {
    if (!result.duplicate) notify(result.message, 'error')
    return
  }
  notify(`Declined ${request.peer_name}.`, 'success')
}

onMounted(() => matchStore.loadInbox())
onUnmounted(() => clearTimeout(redirectTimer))
</script>

<template>
  <AppLayout>
    <template #header-sub>
      <p class="mt-1 text-xs text-[var(--text-secondary)]">{{ headerSub }}</p>
    </template>

    <div class="mx-auto max-w-4xl">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 class="text-2xl font-bold">Swap Requests</h2>
          <p class="mt-1 text-sm text-[var(--text-secondary)]">
            Manage incoming swap proposals and track your sent requests.
          </p>
        </div>

        <button
          type="button"
          class="flex items-center gap-2 rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] transition hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="matchStore.loadingInbox"
          @click="matchStore.loadInbox()"
        >
          <svg
            class="h-4 w-4"
            :class="matchStore.loadingInbox ? 'animate-spin' : ''"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          ><path d="M21 12a9 9 0 1 1-3-6.7" /><path d="M21 3v6h-6" /></svg>
          Reload
        </button>
      </div>

      <div class="mt-6">
        <SwapTabs v-model="activeTab" :tabs="tabs" />
      </div>

      <div v-if="matchStore.error" class="mt-5 flex items-start justify-between gap-4 rounded-lg border border-[var(--danger-border)] bg-[var(--danger-bg)] px-4 py-3 text-xs font-semibold text-[var(--danger-text)]">
        <span>{{ matchStore.error }}</span>
        <button type="button" class="shrink-0 underline transition hover:opacity-70" @click="matchStore.loadInbox()">Try again</button>
      </div>

      <Transition
        enter-active-class="transition duration-300"
        enter-from-class="translate-y-2 opacity-0"
        leave-active-class="transition duration-300"
        leave-to-class="opacity-0"
      >
        <div v-if="toast" class="fixed bottom-6 right-6 z-50 max-w-xs shadow-lg">
          <ToastMessage :message="toast" :type="toastType" @dismiss="toast = ''" />
        </div>
      </Transition>

      <div v-if="loading" class="mt-5 space-y-4">
        <SwapRequestSkeleton />
        <SwapRequestSkeleton />
        <SwapRequestSkeleton />
      </div>

      <div v-else-if="!matchStore.error && !rows.length" class="mt-5">
        <EmptyState
          :title="activeTab === 'received' ? 'No incoming requests' : 'No sent requests yet'"
          :message="activeTab === 'received'
            ? 'When another swapper proposes a session with you, it lands here so you can accept or decline.'
            : 'Send a proposal from Skill Matching and its progress shows up in this tab.'"
        >
          <RouterLink
            v-if="activeTab === 'sent'"
            :to="{ name: 'skill-matching' }"
            class="mt-5 rounded-lg bg-[var(--accent-primary)] px-4 py-2 text-sm font-bold text-white transition hover:bg-[var(--accent-hover)]"
          >Find a skill twin</RouterLink>
        </EmptyState>
      </div>

      <TransitionGroup v-else tag="div" name="list" class="mt-5 space-y-4">
        <SwapRequestCard
          v-for="request in rows"
          :key="request.match_id"
          :request="request"
          :direction="activeTab === 'received' ? 'incoming' : 'sent'"
          :acting="matchStore.actingIds.has(request.match_id)"
          :accepted="matchStore.acceptedIds.has(request.match_id)"
          :fading="matchStore.fadingIds.has(request.match_id)"
          @accept="accept"
          @decline="decline"
        />
      </TransitionGroup>
    </div>
  </AppLayout>
</template>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(24px);
}

.list-leave-active {
  position: absolute;
  width: 100%;
}
</style>
