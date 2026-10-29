<script setup>
const props = defineProps({
  badges: { type: Array, required: true }, // [{ key, name, description, unlocked, progress }]
})

const RING_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-5)',
  'var(--chart-4)',
]

function ring(index) {
  return RING_COLORS[index % RING_COLORS.length]
}
</script>

<template>
  <ul class="grid grid-cols-1 gap-3 sm:grid-cols-2">
    <li
      v-for="(badge, index) in badges"
      :key="badge.key"
      class="group relative flex items-center gap-3 rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] p-3 transition"
      :class="badge.unlocked ? 'hover:border-[var(--accent-primary)]' : 'grayscale opacity-50'"
    >
      <span
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full"
        :style="{
          background: badge.unlocked ? `color-mix(in srgb, ${ring(index)} 18%, transparent)` : 'var(--bg-surface)',
          boxShadow: badge.unlocked ? `0 0 0 2px ${ring(index)}` : 'none',
        }"
      >
        <svg class="h-5 w-5" :style="{ color: badge.unlocked ? ring(index) : 'var(--text-secondary)' }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <template v-if="badge.key === 'active_swapper'"><path d="M8 3 4 7l4 4" /><path d="M4 7h16" /><path d="m16 21 4-4-4-4" /><path d="M20 17H4" /></template>
          <template v-else-if="badge.key === 'knowledge_giver'"><path d="M12 3a5 5 0 0 0-3 9v3h6v-3a5 5 0 0 0-3-9z" /><path d="M9.5 21h5" /><path d="M10.5 18h3" /></template>
          <template v-else-if="badge.key === 'skill_master'"><path d="M12 2 15 9l7 .6-5.3 4.6L18.2 21 12 17.4 5.8 21l1.5-6.8L2 9.6 9 9z" /></template>
          <template v-else-if="badge.key === 'deep_learner'"><path d="M12 7a4 4 0 0 0-8 0v10a4 4 0 0 1 8 0 4 4 0 0 1 8 0V7a4 4 0 0 0-8 0z" /><path d="M12 7v10" /></template>
          <template v-else><path d="M12 2c1.5 3.5-1 5-1 7a3 3 0 0 0 5 2c1.5 1.5 2 3 2 4.5a6 6 0 1 1-11-3.2C9 10 12 8 12 2z" /></template>
        </svg>
      </span>

      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-bold">{{ badge.name }}</p>
        <p class="truncate text-[11px] text-[var(--text-secondary)]" :title="badge.description">{{ badge.description }}</p>
        <div v-if="!badge.unlocked" class="mt-1.5 h-1 overflow-hidden rounded-full bg-[var(--bg-surface)]">
          <div class="h-full rounded-full bg-[var(--accent-primary)] transition-[width] duration-700" :style="{ width: `${badge.progress}%` }" />
        </div>
      </div>

      <span
        class="absolute -top-2 right-2 rounded-md px-1.5 py-0.5 text-[10px] font-bold opacity-0 transition group-hover:opacity-100"
        :class="badge.unlocked ? 'bg-[var(--success-bg)] text-[var(--success-text)]' : 'bg-[var(--bg-surface)] text-[var(--text-secondary)]'"
      >{{ badge.unlocked ? 'Unlocked' : `${Math.round(badge.progress)}% there` }}</span>
    </li>
  </ul>

  <p v-if="!badges.length" class="py-8 text-center text-sm text-[var(--text-secondary)]">Milestones unlock as you complete swaps.</p>
</template>
