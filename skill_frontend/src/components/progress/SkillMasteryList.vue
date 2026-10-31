<script setup>
import { onMounted, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, required: true }, // [{ skill_name, proficiency, percent, verified }]
})

const BAR_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
]

const drawn = ref(false)

function redraw() {
  drawn.value = false
  requestAnimationFrame(() => requestAnimationFrame(() => { drawn.value = true }))
}

onMounted(redraw)
watch(() => props.items.map((item) => item.skill_name).join('|'), redraw)
</script>

<template>
  <ul v-if="items.length" class="space-y-3.5">
    <li v-for="(item, index) in items" :key="item.skill_name" class="flex items-center gap-3">
      <p class="w-24 shrink-0 truncate text-sm font-semibold" :title="item.skill_name">{{ item.skill_name }}</p>
      <div class="h-2.5 min-w-0 flex-1 overflow-hidden rounded-full bg-[var(--bg-base)]">
        <div
          class="h-full rounded-full transition-[width] duration-700 ease-out"
          :style="{ width: drawn ? `${Math.min(100, item.percent)}%` : '0%', background: BAR_COLORS[index % BAR_COLORS.length] }"
        />
      </div>
      <p class="w-32 shrink-0 text-right text-xs font-medium text-[var(--text-secondary)]">
        <span class="font-bold text-[var(--text-primary)]">{{ item.percent }}%</span>
        <span class="mx-1 opacity-40">·</span>{{ item.proficiency }}
        <svg
          v-if="item.verified"
          class="ml-0.5 inline h-3 w-3 text-[var(--success-text)]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-label="Verified by AI interview"
        ><path d="M20 6 9 17l-5-5" /></svg>
      </p>
    </li>
  </ul>
  <p v-else class="rounded-lg border border-dashed border-[var(--border-color)] px-4 py-8 text-center text-sm text-[var(--text-secondary)]">
    No skills listed yet.
    <RouterLink :to="{ name: 'build-profile' }" class="font-semibold text-[var(--accent-primary)] hover:underline">Add a skill</RouterLink>
    to start tracking mastery.
  </p>
</template>
