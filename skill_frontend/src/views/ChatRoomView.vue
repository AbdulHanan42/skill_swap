<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { extractApiError } from '@/api/client'
import { fetchMatchDetail } from '@/api/matchApi'
import AppLayout from '@/components/common/AppLayout.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ScoreRing from '@/components/common/ScoreRing.vue'
import SkillTag from '@/components/common/SkillTag.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import ChatBubble from '@/components/chat/ChatBubble.vue'
import { useAuthStore } from '@/stores/authStore'
import { useChatRoom } from '@/composables/useChatRoom'

const route = useRoute()
const auth = useAuthStore()

const matchId = computed(() => Number(route.params.matchId) || 0)
const peer = ref(null)
const peerError = ref('')

const { messages, loading, error, connected, disconnected, send, connect } =
  useChatRoom(() => matchId.value)

const draft = ref('')
const scroller = ref(null)

const statusLabel = computed(() => {
  if (loading.value) return 'Loading history…'
  if (connected.value) return 'Connected'
  if (disconnected.value) return 'Offline — reconnect'
  return 'Connecting…'
})

const statusClass = computed(() => {
  if (loading.value || !connected.value && !disconnected.value) {
    return 'border-[var(--border-color)] bg-[var(--bg-base)] text-[var(--text-secondary)]'
  }
  return connected.value
    ? 'border-[var(--success-text)]/40 bg-[var(--success-bg)] text-[var(--success-text)]'
    : 'border-[var(--warning-text)]/40 bg-[var(--warning-bg)] text-[var(--warning-text)]'
})

async function loadPeer() {
  if (!matchId.value) return
  peerError.value = ''
  try {
    peer.value = await fetchMatchDetail(matchId.value)
  } catch (err) {
    peerError.value = extractApiError(err)
    peer.value = null
  }
}

watch(matchId, loadPeer, { immediate: true })

watch(
  () => [messages.value.length, loading.value],
  async () => {
    await nextTick()
    const node = scroller.value
    if (node) node.scrollTop = node.scrollHeight
  },
)

function submit() {
  if (!send(draft.value)) return
  draft.value = ''
}
</script>

<template>
  <AppLayout>
    <template #header-sub>
      <p class="mt-1 text-xs text-[var(--text-secondary)]">
        <template v-if="peer">Chatting with <span class="font-semibold text-[var(--text-primary)]">{{ peer.peer_name }}</span> about your swap</template>
        <template v-else>Your swap conversations</template>
      </p>
    </template>

    <div v-if="!matchId" class="mx-auto max-w-3xl">
      <EmptyState
        title="No chat room open"
        message="Chat rooms unlock as soon as a swap request is accepted. Pick a connected partner to start the conversation."
      >
        <RouterLink
          :to="{ name: 'swap-requests' }"
          class="mt-5 rounded-lg bg-[var(--accent-primary)] px-4 py-2 text-sm font-bold text-white transition hover:bg-[var(--accent-hover)]"
        >Go to Swap Requests</RouterLink>
      </EmptyState>
    </div>

    <div v-else-if="peerError" class="mx-auto max-w-3xl rounded-lg border border-[var(--danger-border)] bg-[var(--danger-bg)] px-4 py-3 text-xs font-semibold text-[var(--danger-text)]">
      {{ peerError }}
      <button type="button" class="ml-3 underline" @click="loadPeer">Try again</button>
    </div>

    <div v-else class="mx-auto flex h-[calc(100vh-13rem)] max-w-3xl flex-col overflow-hidden rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] shadow-sm">
      <header class="flex flex-wrap items-center gap-4 border-b border-[var(--border-color)] px-5 py-4">
        <UserAvatar v-if="peer" :name="peer.peer_name" :src="peer.peer_avatar" size="md" />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h2 class="truncate text-base font-bold">{{ peer?.peer_name ?? 'Chat room' }}</h2>
            <span class="text-xs text-[var(--text-secondary)]">{{ peer?.peer_designation }}</span>
          </div>
          <div v-if="peer" class="mt-1.5 flex flex-wrap gap-1.5">
            <SkillTag v-for="skill in peer.offers.slice(0, 3)" :key="`o-${skill}`" :label="skill" variant="offer" />
            <SkillTag v-for="skill in peer.wants.slice(0, 3)" :key="`w-${skill}`" :label="skill" variant="want" />
          </div>
        </div>
        <ScoreRing v-if="peer" :score="Math.round(peer.match_score ?? 0)" :size="54" label="" />
        <button
          type="button"
          class="flex items-center gap-2 rounded-lg border px-3 py-1.5 text-[11px] font-semibold transition"
          :class="statusClass"
          :disabled="connected || loading"
          @click="connect()"
        >
          <span class="h-2 w-2 rounded-full" :class="connected ? 'bg-[var(--success-text)]' : 'bg-current'"></span>
          {{ statusLabel }}
        </button>
      </header>

      <div v-if="error" class="border-b border-[var(--danger-border)] bg-[var(--danger-bg)] px-5 py-2.5 text-xs font-semibold text-[var(--danger-text)]">
        {{ error }}
      </div>

      <div ref="scroller" class="flex-1 space-y-4 overflow-y-auto bg-[var(--bg-base)] px-5 py-5">
        <div v-if="loading" class="space-y-4">
          <div v-for="n in 3" :key="n" class="h-12 w-2/3 animate-pulse rounded-2xl bg-[var(--border-color)]" :class="n % 2 ? '' : 'ml-auto'"></div>
        </div>

        <div v-else-if="!messages.length" class="flex h-full flex-col items-center justify-center text-center">
          <div class="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--accent-primary)]/10 text-xl">💬</div>
          <p class="mt-3 text-sm font-bold">Say hello to {{ peer?.peer_name ?? 'your partner' }}</p>
          <p class="mt-1 max-w-xs text-xs text-[var(--text-secondary)]">Agree what each of you teaches, and schedule the first session.</p>
        </div>

        <ChatBubble
          v-for="message in messages"
          :key="message.id"
          :message="message"
          :mine="message.sender_id === auth.user?.id"
        />
      </div>

      <form class="flex items-center gap-3 border-t border-[var(--border-color)] px-5 py-4" @submit.prevent="submit">
        <input
          v-model="draft"
          type="text"
          maxlength="4000"
          :disabled="!connected"
          :placeholder="connected ? 'Write a message…' : 'Waiting for the connection…'"
          class="min-w-0 flex-1 rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-4 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)] disabled:cursor-not-allowed disabled:opacity-60"
        />
        <button
          type="submit"
          class="flex shrink-0 items-center gap-2 rounded-lg bg-[var(--accent-primary)] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="!connected || !draft.trim()"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
          Send
        </button>
      </form>
    </div>
  </AppLayout>
</template>
