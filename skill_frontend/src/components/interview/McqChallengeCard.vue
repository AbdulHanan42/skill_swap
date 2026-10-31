<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  question: { type: Object, default: null },
  skillLabel: { type: String, required: true },
  busy: { type: Boolean, default: false },
  demo: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'skip'])

const selected = ref(null)

watch(() => props.question?.id, () => { selected.value = null })

function choose(index) {
  if (props.busy) return
  selected.value = index
}

function save() {
  if (selected.value === null || props.busy) return
  emit('submit', selected.value)
}

const LETTERS = ['A', 'B', 'C', 'D', 'E']
</script>

<template>
  <section class="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 shadow-sm sm:p-5">
    <div v-if="!question" class="space-y-3">
      <div class="h-4 w-52 animate-pulse rounded bg-[var(--border-color)]"></div>
      <div class="h-16 animate-pulse rounded-xl bg-[var(--border-color)]"></div>
      <div v-for="n in 4" :key="n" class="h-11 animate-pulse rounded-xl bg-[var(--border-color)]"></div>
    </div>

    <template v-else>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="text-sm font-extrabold">
          {{ skillLabel }} Quiz
          <span class="font-semibold text-[var(--text-secondary)]">— Question {{ question.index }} of {{ question.total }}</span>
        </h3>
        <span
          v-if="demo"
          class="rounded-md bg-[var(--warning-bg)] px-2 py-0.5 text-[10px] font-bold text-[var(--warning-text)]"
          title="The interview service could not be reached, so this paper is running locally."
        >OFFLINE PAPER</span>
      </div>

      <p class="mt-3 rounded-xl border border-[var(--border-color)] bg-[var(--bg-base)] p-4 text-sm font-bold leading-relaxed">
        {{ question.prompt }}
      </p>

      <ul class="mt-3 space-y-2.5">
        <li v-for="(option, index) in question.options" :key="index">
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-xl border p-3 text-left text-sm transition"
            :class="selected === index
              ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 text-[var(--text-primary)] ring-1 ring-[var(--accent-primary)]'
              : 'border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)] hover:border-[var(--accent-primary)]/60 hover:bg-[var(--bg-base)]'"
            :aria-pressed="selected === index"
            :disabled="busy"
            @click="choose(index)"
          >
            <span
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-[11px] font-extrabold"
              :class="selected === index ? 'bg-[var(--accent-primary)] text-white' : 'bg-[var(--bg-base)] text-[var(--text-secondary)]'"
            >{{ LETTERS[index] }}</span>
            <span class="min-w-0 flex-1">{{ option }}</span>
            <span
              v-if="selected === index"
              class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-white"
            >
              <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            </span>
          </button>
        </li>
      </ul>

      <div class="mt-4 flex items-center justify-between gap-3">
        <button
          type="button"
          class="rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-secondary)] transition hover:text-[var(--text-primary)] disabled:opacity-50"
          :disabled="busy"
          @click="emit('skip')"
        >Skip Question</button>
        <button
          type="button"
          class="flex items-center gap-2 rounded-lg bg-[var(--accent-primary)] px-5 py-2.5 text-xs font-bold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="busy || selected === null"
          @click="save"
        >
          <svg v-if="busy" class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.216-8.56"/></svg>
          {{ question.index === question.total ? 'Save & Finish' : 'Save & Next' }}
        </button>
      </div>
    </template>
  </section>
</template>
