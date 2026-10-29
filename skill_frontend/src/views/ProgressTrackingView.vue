<script setup>
import { computed, onMounted, ref } from 'vue'

import { extractApiError } from '@/api/client'
import { getProgressDashboard } from '@/api/progressApi'
import AppLayout from '@/components/common/AppLayout.vue'
import WidgetCard from '@/components/common/WidgetCard.vue'
import ActivityChart from '@/components/progress/ActivityChart.vue'
import BadgeGrid from '@/components/progress/BadgeGrid.vue'
import ProgressStatCard from '@/components/progress/ProgressStatCard.vue'
import SessionTimeline from '@/components/progress/SessionTimeline.vue'
import SkillMasteryList from '@/components/progress/SkillMasteryList.vue'

const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const dashboard = ref(null)

const stats = computed(() => dashboard.value ?? {})

function trimmed(value) {
  const num = Number(value) || 0
  return Number.isInteger(num) ? num.toFixed(0) : num.toFixed(1)
}

function plural(count, word) {
  if (count === 1) return word
  return /(ch|sh|ss|x|z)$/.test(word) ? `${word}es` : `${word}s`
}

const swapHoursValue = computed(() => trimmed(stats.value.swap_hours ?? 0))

const deltaChip = computed(() => {
  const delta = stats.value.swap_hours_delta
  if (delta === null || delta === undefined) {
    return (stats.value.swap_hours ?? 0) > 0 ? 'Active now' : 'No hours yet'
  }
  return `${delta > 0 ? '+' : ''}${delta}% this week`
})

const deltaTone = computed(() => {
  const delta = stats.value.swap_hours_delta
  if (delta === null || delta === undefined) return 'accent'
  if (delta > 0) return 'success'
  if (delta < 0) return 'danger'
  return 'warning'
})

const gradeChip = computed(() => {
  if (!stats.value.ai_interview_count) return 'No tests yet'
  return `Grade: ${stats.value.ai_grade}`
})

const unlockedBadges = computed(() => (stats.value.badges ?? []).filter((b) => b.unlocked).length)

async function load({ silent = false } = {}) {
  if (silent) refreshing.value = true
  else loading.value = true
  error.value = ''
  try {
    dashboard.value = await getProgressDashboard()
  } catch (err) {
    error.value = extractApiError(err)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

onMounted(() => load())
</script>

<template>
  <AppLayout>
    <template #header-sub>
      <p class="mt-1 text-xs text-[var(--text-secondary)]">
        Swap Hrs: <span class="font-semibold text-[var(--text-primary)]">{{ swapHoursValue }}</span>
        <span class="mx-2 opacity-40">|</span>
        Skill Twins: <span class="font-semibold text-[var(--text-primary)]">{{ stats.skill_twins ?? 0 }}</span>
        <span class="mx-2 opacity-40">|</span>
        Streak: <span class="font-semibold text-[var(--text-primary)]">{{ stats.active_streak_days ?? 0 }}d</span>
      </p>
    </template>

    <!-- Page header -->
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 class="text-2xl font-extrabold">Progress Tracking</h2>
        <p class="mt-1 text-sm text-[var(--text-secondary)]">
          Monitor your learning progress, completed swaps, and achievements.
        </p>
      </div>
      <button
        type="button"
        class="flex items-center gap-2 rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] shadow-sm transition hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] disabled:opacity-60"
        :disabled="loading || refreshing"
        @click="load({ silent: true })"
      >
        <svg class="h-3.5 w-3.5" :class="refreshing ? 'animate-spin' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8" /><path d="M21 3v5h-5" /><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16" /><path d="M3 21v-5h5" /></svg>
        Refresh
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-bg)] px-4 py-3 text-sm text-[var(--danger-text)]">
      <span class="font-semibold">Could not load your progress: {{ error }}</span>
      <button type="button" class="rounded-lg border border-[var(--danger-border)] bg-[var(--bg-surface)] px-3 py-1 text-xs font-bold transition hover:opacity-80" @click="load()">Try again</button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="mt-5 space-y-5">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="n in 4" :key="n" class="h-[86px] animate-pulse rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)]" />
      </div>
      <div class="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
        <div v-for="n in 2" :key="n" class="h-64 animate-pulse rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)]" />
      </div>
    </div>

    <Transition name="fade" appear>
      <div v-if="!loading && dashboard && !error" class="mt-5 space-y-5">
        <!-- Stat cards -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <ProgressStatCard
            label="Swap Hours"
            :value="`${swapHoursValue}h`"
            hint="Completed"
            :chip="deltaChip"
            :chip-tone="deltaTone"
          />
          <ProgressStatCard label="Skill Twins" :value="stats.skill_twins ?? 0" :unit="plural(stats.skill_twins ?? 0, 'Match')" value-tone="accent" />
          <ProgressStatCard label="Active Streak" :value="stats.active_streak_days ?? 0" :unit="plural(stats.active_streak_days ?? 0, 'Day')">
            <template #icon>
              <svg class="h-5 w-5 text-[var(--chart-5)]" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2c1.2 3.4-1.6 5.2-1.6 7.4a2.6 2.6 0 0 0 4.3 1.9c1.6 1.6 2.3 3.2 2.3 4.7a5 5 0 1 1-10 0C7 12 12 9.6 12 2z" /></svg>
            </template>
          </ProgressStatCard>
          <ProgressStatCard
            label="AI Interview Avg"
            :value="`${trimmed(stats.ai_interview_average ?? 0)}%`"
            :chip="gradeChip"
            :chip-tone="stats.ai_interview_count ? 'success' : 'accent'"
          />
        </div>

        <!-- Widgets -->
        <div class="grid grid-cols-1 items-start gap-5 xl:grid-cols-2">
          <div class="space-y-5">
            <WidgetCard title="Skill Mastery Progress" :subtitle="`${stats.total_skills_listed ?? 0} ${plural(stats.total_skills_listed ?? 0, 'Skill')} listed`">
              <SkillMasteryList :items="stats.skill_mastery ?? []" />
            </WidgetCard>

            <WidgetCard title="Earned Badges & Milestones" :subtitle="`${unlockedBadges} of ${(stats.badges ?? []).length} unlocked`">
              <BadgeGrid :badges="stats.badges ?? []" />
            </WidgetCard>
          </div>

          <div class="space-y-5">
            <WidgetCard title="Activity & Growth" subtitle="Swap hours over the last 7 days">
              <ActivityChart :points="stats.weekly_activity ?? []" />
            </WidgetCard>

            <WidgetCard title="Completed Swap Sessions" :subtitle="stats.completed_sessions_total ? `${stats.completed_sessions_total} ${plural(stats.completed_sessions_total, 'session')} logged` : 'Nothing logged yet'">
              <SessionTimeline :sessions="stats.completed_sessions ?? []" />
            </WidgetCard>
          </div>
        </div>
      </div>
    </Transition>
  </AppLayout>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
