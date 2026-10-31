<script setup>
import { computed } from 'vue'

const props = defineProps({
  step: { type: Number, required: true },
  answered: { type: Number, default: 0 },
  totalQuestions: { type: Number, default: 5 },
  finished: { type: Boolean, default: false },
})

const STEPS = [
  { title: 'Step 1: Technical MCQs', idle: 'Answer 5 questions' },
  { title: 'Step 2: Practical Coding Task', idle: 'Interactive' },
  { title: 'Step 3: Verification Analysis', idle: 'Locked' },
]

// The node travels along the track as the section it belongs to fills up.
const fill = computed(() => {
  if (props.step === 0) {
    const share = props.totalQuestions ? props.answered / props.totalQuestions : 0
    return Math.min(92, 12 + share * 76)
  }
  return 100
})

const nodeLeft = computed(() => `${fill.value}%`)

function stateFor(index) {
  if (props.finished) return 'done'
  if (index < props.step) return 'done'
  if (index === props.step) return 'active'
  return 'locked'
}

const caption = computed(() => {
  if (props.finished) return 'Verified'
  if (props.step === 0) return `Question ${Math.min(props.answered + 1, props.totalQuestions)} of ${props.totalQuestions}`
  if (props.step === 1) return 'Assigned task'
  return 'Analysis ready'
})

const meta = computed(() =>
  STEPS.map((item, index) => {
    const mode = stateFor(index)
    return {
      ...item,
      mode,
      label:
        index === 0
          ? mode === 'done'
            ? 'Completed'
            : 'Active/In-Progress'
          : index === 1
            ? mode === 'locked'
              ? 'Up next'
              : mode === 'done'
                ? 'Submitted'
                : 'Ready for your upload'
            : mode === 'locked'
              ? 'Locked'
              : 'Verification Analysis',
      foot: index === props.step ? caption.value : index < props.step ? 'Signed off' : item.idle,
    }
  }),
)
</script>

<template>
  <ol class="grid w-full grid-cols-1 gap-4 sm:grid-cols-3">
    <li v-for="(item, index) in meta" :key="item.title">
      <p class="text-xs font-extrabold sm:text-sm" :class="item.mode === 'locked' ? 'text-[var(--text-secondary)]' : 'text-[var(--text-primary)]'">
        {{ item.title }}
      </p>
      <p class="text-[11px] font-medium text-[var(--text-secondary)]">{{ item.label }}</p>

      <div class="relative mt-2 h-1.5 rounded-full" :class="item.mode === 'locked' ? 'bg-[var(--border-color)]' : 'bg-[var(--accent-primary)]/20'">
        <div
          class="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
          :class="item.mode === 'done' ? 'bg-[var(--success-text)]' : item.mode === 'active' ? 'bg-[var(--accent-primary)]' : 'bg-transparent'"
          :style="{ width: item.mode === 'locked' ? '0%' : `${item.mode === 'done' ? 100 : fill}%` }"
        ></div>
        <span
          v-if="item.mode !== 'locked'"
          class="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 bg-[var(--bg-surface)] transition-all duration-500"
          :class="item.mode === 'done' ? 'border-[var(--success-text)]' : 'border-[var(--accent-primary)]'"
          :style="{ left: item.mode === 'done' ? '100%' : nodeLeft }"
        ></span>
        <svg v-else class="absolute right-0 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      </div>

      <p class="mt-2 text-[11px] font-semibold" :class="item.mode === 'active' ? 'text-[var(--accent-primary)]' : 'text-[var(--text-secondary)]'">
        {{ item.foot }}
      </p>
    </li>
  </ol>
</template>
