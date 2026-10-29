<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { listSkillCatalog } from '@/api/profileApi'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()

/* -- theme -- */

const isDarkMode = ref(localStorage.getItem('skillswap_theme') === 'dark')

function applyTheme() {
  document.documentElement.classList.toggle('dark', isDarkMode.value)
  localStorage.setItem('skillswap_theme', isDarkMode.value ? 'dark' : 'light')
}

function toggleTheme(dark) {
  isDarkMode.value = dark
  applyTheme()
}

/* ---------- dynamic user data ---------- */

const skillNames = ref({})

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] ?? 'there')

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

const navItems = [
  { label: 'Dashboard', icon: 'grid', active: true },
  { label: 'Build Profile', icon: 'user' },
  { label: 'Skill Matching', icon: 'swap' },
  { label: 'Chat Room', icon: 'chat' },
  { label: 'AI Interview', icon: 'gear' },
  { label: 'Progress Tracking', icon: 'chart' },
]

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

/* -- actions  */

function goAuth() {
  auth.logout()
  router.push({ name: 'auth' })
}

onMounted(async () => {
  applyTheme()
  if (!auth.user) {
    try {
      await auth.loadProfile()
    } catch {
      goAuth()
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
  <div class="flex min-h-screen bg-[var(--bg-base)] text-[var(--text-primary)]">
    <!-- ============ Sidebar ============ -->
    <aside class="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-[var(--border-color)] bg-[var(--bg-surface)] p-4 lg:flex">
      <div class="mb-8 flex items-center gap-2.5 px-2 pt-1">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--accent-primary)] text-lg font-bold text-white">⇄</div>
        <span class="text-lg font-bold">Skill Swap</span>
      </div>

      <nav class="flex-1 space-y-1">
        <button
          v-for="item in navItems"
          :key="item.label"
          type="button"
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
          :class="item.active
            ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]'
            : 'text-[var(--text-secondary)] hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]'"
        >
          <svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <template v-if="item.icon === 'grid'"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></template>
            <template v-else-if="item.icon === 'user'"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></template>
            <template v-else-if="item.icon === 'swap'"><path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></template>
            <template v-else-if="item.icon === 'chat'"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></template>
            <template v-else-if="item.icon === 'gear'"><circle cx="12" cy="12" r="3"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></template>
            <template v-else><path d="m3 17 6-6 4 4 8-8"/><path d="M14 7h7v7"/></template>
          </svg>
          {{ item.label }}
        </button>
      </nav>

      <div class="space-y-1 border-t border-[var(--border-color)] pt-4">
        <button type="button" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="9"/></svg>
          Account
        </button>
        <button type="button" class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-red-500" @click="goAuth">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/></svg>
          Log out
        </button>
      </div>
    </aside>

    <!-- ============ Main ============ -->
    <div class="flex min-w-0 flex-1 flex-col">
      <!-- Header -->
      <header class="border-b border-[var(--border-color)] bg-[var(--bg-surface)] px-5 py-4 lg:px-8">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 class="text-xl font-bold lg:text-2xl">Hello, {{ firstName }}! Let's swap skills today</h1>
            <p class="mt-1 text-xs text-[var(--text-secondary)]">
              Swap Hrs: <span class="font-semibold text-[var(--text-primary)]">24</span>
              <span class="mx-2 opacity-40">|</span>
              Skill Twins: <span class="font-semibold text-[var(--text-primary)]">5</span>
            </p>
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

            <button type="button" class="relative rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] p-2 text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
              <span class="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-[var(--bg-surface)]"></span>
            </button>

            <div class="flex items-center gap-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--accent-primary)] text-sm font-bold text-white">{{ userInitial }}</div>
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

      <!-- Widgets grid -->
      <main class="grid flex-1 grid-cols-1 items-start gap-5 p-5 lg:px-8 xl:grid-cols-3">
        <!-- Welcome Banner -->
        <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
          <h2 class="mb-4 text-sm font-bold">Welcome Banner <span class="font-normal text-[var(--text-secondary)]">(Summary Card)</span></h2>
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-lg font-bold text-white">{{ userInitial }}</div>
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold">{{ auth.user?.full_name ?? '—' }} <span class="font-normal text-[var(--text-secondary)]">(Full Stack dev)</span> • Level 4</p>
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
            <span v-for="skill in offers" :key="skill" class="rounded-lg bg-[var(--success-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--success-text)]">{{ skill }}</span>
            <span v-if="!offers.length" class="text-xs italic text-[var(--text-secondary)]">No offers yet</span>
          </div>
          <p class="mt-4 text-xs font-semibold">What I Want (Wants):</p>
          <div class="mt-2 flex flex-wrap gap-2">
            <span v-for="skill in wants" :key="skill" class="rounded-lg bg-[var(--warning-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--warning-text)]">{{ skill }}</span>
            <span v-if="!wants.length" class="text-xs italic text-[var(--text-secondary)]">No wants yet</span>
            <button type="button" class="rounded-lg border border-dashed border-[var(--accent-primary)] px-2.5 py-1 text-xs font-semibold text-[var(--accent-primary)] transition hover:bg-[var(--accent-primary)]/10">+ Add Skill</button>
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
      </main>
    </div>
  </div>
</template>
