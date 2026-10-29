<script setup>
import { computed, onMounted, ref } from 'vue'

import { extractApiError } from '@/api/client'
import EmptyState from '@/components/common/EmptyState.vue'
import ToastMessage from '@/components/common/ToastMessage.vue'
import AppLayout from '@/components/common/AppLayout.vue'
import MatchCard from '@/components/matching/MatchCard.vue'
import MatchFilterBar from '@/components/matching/MatchFilterBar.vue'
import MatchProfileModal from '@/components/matching/MatchProfileModal.vue'
import TopMatchCard from '@/components/matching/TopMatchCard.vue'
import { useSwapRequests } from '@/composables/useSwapRequests'
import { fetchMatchSuggestions, listSkillCatalog } from '@/api/profileApi'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()

/* ---------- state ---------- */

const matches = ref([]) // { user_id, name, designation, avatar, bio, score, offers[], wants[], proficiencies[] }
const isLoading = ref(true)
const loadError = ref('')

const search = ref('')
const sortMode = ref('highest')
const levelFilter = ref('all')

const { sentIds, pendingIds, toast, error, request } = useSwapRequests()

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

onMounted(async () => {
  if (!auth.user) {
    await auth.loadProfile().catch(() => {})
  }
  loadMatches()
})

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
        <p v-if="loadError" class="rounded-lg border border-red-300 bg-red-50 px-4 py-2.5 text-xs font-semibold text-red-600">{{ loadError }}</p>
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
          :sent="sentIds.has(topMatch.user_id)"
          :pending="pendingIds.has(topMatch.user_id)"
          @request-swap="request(topMatch.user_id, topMatch.name)"
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
              :sent="sentIds.has(m.user_id)"
              :pending="pendingIds.has(m.user_id)"
              @request-swap="request(m.user_id, m.name)"
              @view-profile="viewingId = m.user_id"
            />
          </div>
        </template>
      </template>
    </div>

    <!-- Profile modal -->
    <MatchProfileModal
      :match="viewing"
      :sent="viewing ? sentIds.has(viewing.user_id) : false"
      :pending="viewing ? pendingIds.has(viewing.user_id) : false"
      @close="viewingId = null"
      @request-swap="request(viewing.user_id, viewing.name); viewingId = null"
    />
  </AppLayout>
</template>
