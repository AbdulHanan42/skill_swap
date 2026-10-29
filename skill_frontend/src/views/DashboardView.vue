<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { listSkillCatalog } from '@/api/profileApi'
import AppLayout from '@/components/common/AppLayout.vue'
import SkillTag from '@/components/common/SkillTag.vue'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()

/* ---------- dynamic user data ---------- */

const skillNames = ref({})

const offers = computed(() =>
  (auth.user?.skills ?? [])
    .filter((s) => s.skill_type === 'OFFERS')
    .map((s) => skillNames.value[s.skill_id] ?? `Skill #${s.skill_id}`),
)

const wants = computed(() =>
  (auth.user?.skills ?? [])
    .filter((s) => s.skill_type === 'WANTS')
    .map((s) => skillNames.value[s.skill_id] ?? `Skill #${s.skill_id}`),
)

const userInitial = computed(() => (auth.user?.full_name ?? 'U').trim().charAt(0).toUpperCase())

/* ---- static widget data (backend integration pending) ----*/

const matches = [
  { name: 'Sarah J.', expert: 'Expert PHP', wants: 'Wants: Vue.js', score: 96, tone: '#f59e0b' },
  { name: 'Omar R.', expert: 'Expert Figma', wants: 'Wants: Tailwind', score: 91, tone: '#10b981' },
]

const upcomingSwaps = [
  { topic: 'PHP session with Sarah J.', time: 'Today, 4:00 PM', tone: '#6366f1' },
  { topic: 'Design review with Omar R.', time: 'Tomorrow, 11:00 AM', tone: '#f59e0b' },
]

const chatPeers = [
  { name: 'Sarah J.', message: 'Can we move our swap to 6 PM?', tone: '#6366f1' },
  { name: 'Omar R.', message: 'Shared the Figma file with you!', tone: '#10b981' },
]

const chartPoints = [
  { day: 'Sun', hours: 2 },
  { day: 'Mon', hours: 5 },
  { day: 'Tue', hours: 3 },
  { day: 'Wed', hours: 7 },
  { day: 'Thu', hours: 5 },
  { day: 'Fri', hours: 8 },
  { day: 'Sat', hours: 6 },
  { day: 'Sun', hours: 9 },
]

const chartPath = computed(() => {
  const max = Math.max(...chartPoints.map((p) => p.hours))
  return chartPoints
    .map((p, i) => {
      const x = 8 + (i * 234) / (chartPoints.length - 1)
      const y = 88 - (p.hours / max) * 70
      return `${i === 0 ? 'M' : 'L'}${x},${y}`
    })
    .join(' ')
})

onMounted(async () => {
  if (!auth.user) {
    try {
      await auth.loadProfile()
    } catch {
      auth.logout()
      router.push({ name: 'auth' })
      return
    }
  }
  try {
    const skills = await listSkillCatalog()
    skillNames.value = Object.fromEntries(skills.map((s) => [s.id, s.name]))
  } catch {
    // catalog is decorative-only; skill tags fall back to ids
  }
})
</script>

<template>
  <AppLayout>
    <!-- Widgets grid -->
    <div class="grid grid-cols-1 items-start gap-5 xl:grid-cols-3">
      <!-- Welcome Banner -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="mb-4 text-sm font-bold">Welcome Banner <span class="font-normal text-[var(--text-secondary)]">(Summary Card)</span></h2>
        <div class="flex items-center gap-3">
          <img v-if="auth.user?.avatar" :src="auth.user.avatar" alt="Your avatar" class="h-12 w-12 shrink-0 rounded-full object-cover" />
          <div v-else class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-lg font-bold text-white">{{ userInitial }}</div>
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold">{{ auth.user?.full_name ?? '—' }} <span class="font-normal text-[var(--text-secondary)]">({{ auth.user?.designation || 'Full Stack dev' }})</span> • Level 4</p>
            <div class="mt-1 flex flex-wrap gap-1.5">
              <span class="rounded-md bg-[var(--success-bg)] px-2 py-0.5 text-[11px] font-semibold text-[var(--success-text)]">Active Swapper</span>
              <span v-for="skill in offers.slice(0, 2)" :key="skill" class="rounded-md bg-[var(--accent-primary)]/10 px-2 py-0.5 text-[11px] font-semibold text-[var(--accent-primary)]">{{ skill }}</span>
              <span v-if="!offers.length" class="rounded-md bg-[var(--accent-primary)]/10 px-2 py-0.5 text-[11px] font-semibold text-[var(--accent-primary)]">Vue Specialist</span>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <div class="mb-1.5 flex justify-between text-xs text-[var(--text-secondary)]">
            <span>Current progress to next swap milestone:</span>
            <span class="font-semibold text-[var(--text-primary)]">16 / 50</span>
          </div>
          <div class="h-2 overflow-hidden rounded-full bg-[var(--bg-base)]">
            <div class="h-full w-[32%] rounded-full bg-[var(--accent-primary)] transition-all duration-700" />
          </div>
        </div>
      </section>

      <!-- Smart Recommendations -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="text-sm font-bold">Smart Recommendations &amp; Swap Matches</h2>
        <p class="mt-1 text-xs text-[var(--text-secondary)]">Active pair-matching visual matching users' request workflows.</p>
        <div class="mt-4 space-y-3">
          <div v-for="m in matches" :key="m.name" class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)]/40 p-3.5">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white" :style="{ background: m.tone }">{{ m.name.charAt(0) }}</div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold">{{ m.name }} - {{ m.expert }}</p>
                <p class="text-xs text-[var(--text-secondary)]">({{ m.wants }})</p>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold text-emerald-500">{{ m.score }}%</p>
                <p class="text-[10px] text-[var(--text-secondary)]">Swap Match Score</p>
              </div>
            </div>
            <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-[var(--bg-base)]">
              <div class="h-full rounded-full bg-emerald-500" :style="{ width: `${m.score}%` }" />
            </div>
            <div class="mt-3 grid grid-cols-2 gap-2">
              <button type="button" class="rounded-lg border border-[var(--accent-primary)] px-3 py-1.5 text-xs font-semibold text-[var(--accent-primary)] transition hover:bg-[var(--accent-primary)]/10">Message</button>
              <button type="button" class="rounded-lg bg-[var(--accent-primary)] px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-[var(--accent-hover)]">Request Swap</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Chat & Scheduled Learning -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="text-sm font-bold">Chat &amp; Scheduled Learning</h2>
        <p class="mt-1 text-xs font-semibold text-[var(--text-secondary)]">Learning Matches</p>
        <div class="mt-2 space-y-2.5">
          <div v-for="(peer, i) in chatPeers" :key="peer.name" class="flex items-center gap-2.5" :class="i % 2 ? 'flex-row-reverse text-right' : ''">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white" :style="{ background: peer.tone }">{{ peer.name.charAt(0) }}</div>
            <div class="rounded-xl rounded-tl-none border border-[var(--border-color)] bg-[var(--accent-primary)]/10 px-3 py-2">
              <p class="text-xs font-semibold">{{ peer.name }}</p>
              <p class="text-[11px] text-[var(--text-secondary)]">{{ peer.message }}</p>
            </div>
          </div>
        </div>
        <p class="mt-5 text-xs font-semibold text-[var(--text-secondary)]">Upcoming Swaps</p>
        <div class="mt-2 space-y-2.5">
          <div v-for="swap in upcomingSwaps" :key="swap.topic" class="flex items-center gap-2.5">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white" :style="{ background: swap.tone }">{{ swap.topic.charAt(0) }}</div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-xs font-semibold">{{ swap.topic }}</p>
              <p class="text-[11px] text-[var(--text-secondary)]">{{ swap.time }}</p>
            </div>
            <button type="button" class="rounded-lg bg-[var(--accent-primary)] px-3 py-1.5 text-[11px] font-semibold text-white transition hover:bg-[var(--accent-hover)]">Join Call</button>
          </div>
        </div>
      </section>

      <!-- Profile & Skills -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="text-sm font-bold">Profile &amp; Skills <span class="font-normal text-[var(--text-secondary)]">(My Skill Portfolio)</span></h2>
        <p class="mt-4 text-xs font-semibold">What I Teach (Offers):</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <SkillTag v-for="skill in offers" :key="skill" :label="skill" variant="offer" size="md" />
          <span v-if="!offers.length" class="text-xs italic text-[var(--text-secondary)]">No offers yet</span>
        </div>
        <p class="mt-4 text-xs font-semibold">What I Want (Wants):</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <SkillTag v-for="skill in wants" :key="skill" :label="skill" variant="want" size="md" />
          <span v-if="!wants.length" class="text-xs italic text-[var(--text-secondary)]">No wants yet</span>
          <RouterLink :to="{ name: 'build-profile' }" class="rounded-lg border border-dashed border-[var(--accent-primary)] px-2.5 py-1 text-xs font-semibold text-[var(--accent-primary)] transition hover:bg-[var(--accent-primary)]/10">+ Add Skill</RouterLink>
        </div>
      </section>

      <!-- AI Advisor -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <h2 class="text-sm font-bold">AI Advisor <span class="font-normal text-[var(--text-secondary)]">(Interviews &amp; Suggestions)</span></h2>
          <span class="text-[var(--text-secondary)]">⋯</span>
        </div>
        <p class="mt-1 text-xs text-[var(--text-secondary)]">Step 6 &amp; 7 AI assessments:</p>
        <div class="mt-4 flex items-center justify-between rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)]/50 p-3">
          <div>
            <p class="text-sm font-semibold">Last Quiz: Python</p>
            <p class="text-xs text-[var(--text-secondary)]">(Grade: A, Score: 88/100)</p>
          </div>
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--success-bg)] text-sm font-bold text-[var(--success-text)]">A</div>
        </div>
        <div class="mt-3 rounded-xl rounded-bl-none bg-[var(--accent-primary)]/10 p-3">
          <p class="text-xs leading-relaxed text-[var(--text-primary)]">
            <span class="font-semibold text-[var(--accent-primary)]">AI Says:</span> Excelled at OOP!<br />
            Suggested Next: Explore PostgreSQL
          </p>
        </div>
        <button type="button" class="mt-4 w-full rounded-lg bg-[var(--accent-primary)] py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--accent-hover)]">Start Interview</button>
      </section>

      <!-- Progress Tracking -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <div class="flex items-start justify-between">
          <h2 class="text-sm font-bold">Progress Tracking</h2>
          <span class="text-[var(--text-secondary)]">⋯</span>
        </div>
        <div class="mt-2 flex items-center justify-between">
          <p class="text-xs font-semibold text-[var(--text-secondary)]">Active Swapping hours</p>
          <span class="rounded-md bg-[var(--success-bg)] px-2 py-0.5 text-[11px] font-bold text-[var(--success-text)]">+2,880 ↗</span>
        </div>
        <svg viewBox="0 0 250 100" class="mt-3 w-full">
          <line x1="8" y1="92" x2="242" y2="92" stroke="var(--border-color)" stroke-width="1" />
          <text x="4" y="30" font-size="8" fill="var(--text-secondary)">100</text>
          <text x="8" y="62" font-size="8" fill="var(--text-secondary)">50</text>
          <rect
            v-for="(p, i) in chartPoints"
            :key="`bar-${i}`"
            :x="11 + i * 30"
            :y="92 - p.hours * 7"
            width="14"
            :height="p.hours * 7"
            rx="2"
            fill="var(--accent-primary)"
            fill-opacity="0.25"
          />
          <path :d="chartPath" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
          <text v-for="(p, i) in chartPoints" :key="`lbl-${i}`" :x="12 + (i * 234) / (chartPoints.length - 1)" y="99" font-size="7" fill="var(--text-secondary)">{{ p.day }}</text>
        </svg>
        <p class="mt-4 text-xs font-semibold text-[var(--text-secondary)]">Unlockable Badges</p>
        <div class="mt-2 flex gap-2.5">
          <span v-for="(badge, i) in [true, false, false, false]" :key="i" class="flex h-8 w-8 items-center justify-center">
            <svg viewBox="0 0 24 24" class="h-7 w-7" :class="badge ? '' : 'opacity-30 grayscale'">
              <path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3z" :fill="badge ? '#f59e0b' : 'var(--border-color)'" />
              <path d="m9 12 2 2 4-4" :stroke="badge ? '#fff' : 'var(--text-secondary)'" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </div>
      </section>
    </div>
  </AppLayout>
</template>
