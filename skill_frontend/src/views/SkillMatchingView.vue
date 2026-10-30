<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { extractApiError } from '@/api/client'
import EmptyState from '@/components/common/EmptyState.vue'
import ToastMessage from '@/components/common/ToastMessage.vue'
import AppLayout from '@/components/common/AppLayout.vue'
import MatchCard from '@/components/matching/MatchCard.vue'
import MatchFilterBar from '@/components/matching/MatchFilterBar.vue'
import MatchProfileModal from '@/components/matching/MatchProfileModal.vue'
import TopMatchCard from '@/components/matching/TopMatchCard.vue'
import { useSwapRequests } from '@/composables/useSwapRequests'
import { fetchMatchSuggestions } from '@/api/matchApi'
import { listSkillCatalog } from '@/api/profileApi'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()

/* ---------- state ---------- */

const matches = ref([]) // { user_id, name, designation, avatar, bio, score, offers[], wants[], proficiencies[] }
const isLoading = ref(true)
const loadError = ref('')

const search = ref('')
const sortMode = ref('highest')
const levelFilter = ref('all')

let stateTimer = null

const { pendingIds, toast, error, request } = useSwapRequests()

/* ---------- load ---------- */

async function loadMatches() {
  isLoading.value = true
  loadError.value = ''
  try {
    const [suggestions, catalog] = await Promise.all([
      fetchMatchSuggestions(),
      listSkillCatalog().catch(() => []),
    ])
    const nameById = Object.fromEntries(catalog.map((s) => [s.id, s.name]))
    matches.value = suggestions.map((item) => ({
      user_id: item.user.id,
      name: item.user.full_name,
      designation: item.user.designation || 'Skill Swapper',
      avatar: item.user.avatar || '',
      bio: item.user.bio || '',
      score: Math.round(item.match_score),
      request_state: item.request_state,
      offers: item.user.skills
        .filter((s) => s.skill_type === 'OFFERS')
        .map((s) => nameById[s.skill_id] ?? `Skill #${s.skill_id}`),
      wants: item.user.skills
        .filter((s) => s.skill_type === 'WANTS')
        .map((s) => nameById[s.skill_id] ?? `Skill #${s.skill_id}`),
      proficiencies: item.user.skills.map((s) => s.proficiency),
    }))
  } catch (err) {
    loadError.value = extractApiError(err)
  } finally {
    isLoading.value = false
  }
}

async function refreshStates() {
  // The peer may have answered while this page stayed open, so re-read the
  // server-side state without flashing the full-page skeleton.
  if (isLoading.value || document.hidden) return
  try {
    const suggestions = await fetchMatchSuggestions()
    const stateById = Object.fromEntries(suggestions.map((item) => [item.user.id, item.request_state]))
    for (const match of matches.value) {
      const next = stateById[match.user_id]
      if (next) match.request_state = next
    }
  } catch {
    /* keep the last known state */
  }
}

onMounted(async () => {
  if (!auth.user) {
    await auth.loadProfile().catch(() => {})
  }
  loadMatches()
  stateTimer = setInterval(refreshStates, 20000)
  document.addEventListener('visibilitychange', refreshStates)
})

onUnmounted(() => {
  clearInterval(stateTimer)
  document.removeEventListener('visibilitychange', refreshStates)
})

/* ---------- swap requests ---------- */

function stateOf(match) {
  if (!match) return 'available'
  if (pendingIds.value.has(match.user_id)) return 'sending'
  return match.request_state || 'available'
}

async function sendRequest(match) {
  if (!match) return
  if (match.request_state === 'requested_by_them') {
    router.push({ name: 'swap-requests' })
    return
  }
  const state = await request(match.user_id, match.name)
  if (state) match.request_state = state
}

/* ---------- filtering ---------- */

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = matches.value
  if (q) {
    list = list.filter(
      (m) =>
        m.name.toLowerCase().includes(q) ||
        m.designation.toLowerCase().includes(q) ||
        m.offers.some((s) => s.toLowerCase().includes(q)) ||
        m.wants.some((s) => s.toLowerCase().includes(q)),
    )
  }
  if (levelFilter.value !== 'all') {
    list = list.filter((m) => m.proficiencies.includes(levelFilter.value))
  }
  return [...list].sort((a, b) =>
    sortMode.value === 'highest' ? b.score - a.score : a.score - b.score,
  )
})

const topMatch = computed(() => filtered.value[0] ?? null)
const otherMatches = computed(() => filtered.value.slice(1))

/* ---------- profile modal ---------- */

const viewingId = ref(null)
const viewing = computed(() => matches.value.find((m) => m.user_id === viewingId.value) ?? null)
</script>

<template>
  <AppLayout>
    <template #header-sub>
      <span class="font-semibold text-[var(--text-primary)]">{{ matches.length }} skill twins found</span>
    </template>

    <div class="mx-auto w-full max-w-5xl">
      <!-- Page header -->
      <h2 class="text-2xl font-bold">Find Your Skill Twin</h2>
      <p class="mt-1 text-sm text-[var(--text-secondary)]">AI-powered matches based on your portfolio.</p>

      <!-- Toasts / errors -->
      <div class="mt-4 space-y-2">
        <ToastMessage v-if="toast" :message="toast" @dismiss="toast = ''" />
        <ToastMessage v-if="error" :message="error" type="error" @dismiss="error = ''" />
        <p v-if="loadError" class="rounded-lg border border-[var(--danger-border)] bg-[var(--danger-bg)] px-4 py-2.5 text-xs font-semibold text-[var(--danger-text)]">{{ loadError }}</p>
      </div>

      <!-- Filter bar -->
      <div class="mt-5">
        <MatchFilterBar
          v-model:search="search"
          v-model:sort="sortMode"
          v-model:level="levelFilter"
        />
      </div>

      <!-- Loading skeleton -->
      <div v-if="isLoading" class="mt-6 space-y-6">
        <div class="h-44 animate-pulse rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)]" />
        <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div v-for="i in 3" :key="i" class="h-56 animate-pulse rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)]" />
        </div>
      </div>

      <!-- Empty state -->
      <EmptyState
        v-else-if="!filtered.length"
        class="mt-6"
        title="No matches found yet"
        :message="matches.length
          ? 'Try a different search term or clear the filters to see your skill twins.'
          : 'Add skills you can teach and skills you want to learn — our matching engine pairs you with people whose portfolio crosses over with yours.'"
      >
        <RouterLink v-if="!matches.length" :to="{ name: 'build-profile' }" class="mt-5 rounded-lg bg-[var(--accent-primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--accent-hover)]">Build Your Profile</RouterLink>
        <button v-else type="button" class="mt-5 rounded-lg border border-[var(--accent-primary)] px-5 py-2.5 text-sm font-semibold text-[var(--accent-primary)] transition hover:bg-[var(--accent-primary)]/10" @click="search = ''; levelFilter = 'all'">Clear filters</button>
      </EmptyState>

      <template v-else>
        <!-- Featured top AI match -->
        <TopMatchCard
          :match="topMatch"
          :state="stateOf(topMatch)"
          @request-swap="sendRequest(topMatch)"
          @view-profile="viewingId = topMatch.user_id"
        />

        <!-- Other matches -->
        <template v-if="otherMatches.length">
          <h3 class="mt-8 text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">Other Recommended Matches</h3>
          <div class="mt-3 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            <MatchCard
              v-for="m in otherMatches"
              :key="m.user_id"
              :match="m"
              :state="stateOf(m)"
              @request-swap="sendRequest(m)"
              @view-profile="viewingId = m.user_id"
            />
          </div>
        </template>
      </template>
    </div>

    <!-- Profile modal -->
    <MatchProfileModal
      :match="viewing"
      :state="stateOf(viewing)"
      @close="viewingId = null"
      @request-swap="sendRequest(viewing)"
    />
  </AppLayout>
</template>
