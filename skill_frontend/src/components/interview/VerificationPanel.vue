<script setup>
import { computed, ref } from 'vue'

import ScoreRing from '@/components/common/ScoreRing.vue'
import { formatBytes } from '@/utils/files'
import { formatChatStamp } from '@/utils/time'

const props = defineProps({
  result: { type: Object, required: true },
})

const emit = defineEmits(['retake'])

const LETTERS = ['A', 'B', 'C', 'D', 'E']
const open = ref(null)

const verdict = computed(() => {
  const score = props.result.score ?? 0
  if (score >= 80) return { tone: 'success', text: 'Verified — strong technical grounding.' }
  if (score >= 60) return { tone: 'warning', text: 'Verified with notes — review the misses below.' }
  return { tone: 'danger', text: 'Needs another pass before this shows on your profile.' }
})

function optionLetter(index) {
  return LETTERS[index] ?? '?'
}
</script>

<template>
  <section class="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 shadow-sm sm:p-5">
    <div class="flex flex-wrap items-center gap-4">
      <ScoreRing :score="result.score" :size="86" label="Technical" />
      <div class="min-w-0 flex-1">
        <h3 class="text-sm font-extrabold">
          Verification Analysis
          <span class="rounded-md bg-[var(--accent-primary)]/15 px-1.5 py-0.5 text-[10px] font-extrabold text-[var(--accent-primary)]">Grade {{ result.grade }}</span>
        </h3>
        <p class="mt-1 text-xs" :class="verdict.tone === 'success' ? 'text-[var(--success-text)]' : verdict.tone === 'warning' ? 'text-[var(--warning-text)]' : 'text-[var(--danger-text)]'">
          {{ verdict.text }}
        </p>
        <p class="mt-1 text-[11px] text-[var(--text-secondary)]">
          {{ result.correct }} of {{ result.total }} correct
          <span v-if="result.skipped"> · {{ result.skipped }} skipped</span>
          <span v-if="result.completed_at"> · {{ formatChatStamp(result.completed_at) }}</span>
          <span v-if="result.graded_by"> · graded by {{ result.graded_by }}</span>
        </p>
      </div>
      <button
        type="button"
        class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2 text-xs font-bold text-[var(--text-secondary)] transition hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)]"
        @click="emit('retake')"
      >Retake interview</button>
    </div>

    <div v-if="result.per_skill?.length" class="mt-4 grid gap-3 sm:grid-cols-2">
      <div v-for="item in result.per_skill" :key="item.skill" class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-base)] p-3">
        <div class="flex items-center justify-between text-xs font-bold">
          <span class="capitalize">{{ item.skill }}</span>
          <span class="text-[var(--text-secondary)]">{{ item.correct }}/{{ item.total }}</span>
        </div>
        <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-[var(--border-color)]">
          <div
            class="h-full rounded-full bg-[var(--accent-primary)] transition-all duration-500"
            :style="{ width: `${item.total ? (item.correct / item.total) * 100 : 0}%` }"
          ></div>
        </div>
      </div>
    </div>

    <p v-if="result.feedback" class="mt-4 rounded-xl bg-[var(--bg-base)] p-3 text-xs leading-relaxed text-[var(--text-primary)]">{{ result.feedback }}</p>

    <p v-if="result.submission" class="mt-3 flex items-center gap-2 text-[11px] text-[var(--text-secondary)]">
      <svg class="h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
      {{ result.submission.filename }} ({{ formatBytes(result.submission.size) }}) filed with your result
    </p>

    <ul class="mt-4 space-y-2">
      <li v-for="(item, index) in result.review" :key="index" class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-base)]">
        <button type="button" class="flex w-full items-start gap-3 p-3 text-left" :aria-expanded="open === index" @click="open = open === index ? null : index">
          <span
            class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-white"
            :class="item.correct ? 'bg-[var(--success-text)]' : 'bg-[var(--danger-text)]'"
          >
            <svg v-if="item.correct" class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            <svg v-else class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </span>
          <span class="min-w-0 flex-1 text-xs font-bold leading-relaxed">{{ item.prompt }}</span>
          <span class="shrink-0 text-[10px] font-semibold uppercase text-[var(--text-secondary)]">{{ item.skipped ? 'skipped' : item.correct ? 'correct' : 'yours' }}</span>
        </button>
        <div v-if="open === index" class="space-y-1.5 border-t border-[var(--border-color)] p-3 text-[11px]">
          <p v-for="(option, optionIndex) in item.options" :key="optionIndex" class="flex gap-2">
            <span class="font-extrabold text-[var(--text-secondary)]">{{ optionLetter(optionIndex) }}.</span>
            <span
              class="min-w-0 flex-1"
              :class="optionIndex === item.answer_index
                ? 'font-bold text-[var(--success-text)]'
                : optionIndex === item.selected && !item.correct
                  ? 'font-bold text-[var(--danger-text)]'
                  : 'text-[var(--text-secondary)]'"
            >{{ option }}</span>
          </p>
          <p v-if="item.explanation" class="pt-1 italic text-[var(--text-secondary)]">{{ item.explanation }}</p>
        </div>
      </li>
    </ul>
  </section>
</template>
