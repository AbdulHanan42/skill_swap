<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, required: true },
  size: { type: Number, default: 80 },
  label: { type: String, default: 'Match Score' },
})

const R = 34
const circumference = computed(() => 2 * Math.PI * R)
const value = computed(() => Math.min(100, Math.max(0, props.score)))
</script>

<template>
  <div class="relative shrink-0" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg viewBox="0 0 80 80" class="h-full w-full -rotate-90">
      <circle cx="40" cy="40" r="34" fill="none" stroke="var(--border-color)" stroke-width="7" />
      <circle
        cx="40" cy="40" r="34" fill="none" stroke="var(--accent-primary)" stroke-width="7" stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="circumference * (1 - value / 100)"
      />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-lg font-bold">{{ Math.round(value) }}%</span>
      <span v-if="label" :class="size < 60 ? 'text-[8px]' : 'text-[9px]'" class="text-[var(--text-secondary)]">{{ label }}</span>
    </div>
  </div>
</template>
