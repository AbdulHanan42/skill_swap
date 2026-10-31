<script setup>
import { computed, ref, watch } from 'vue'

import { formatBytes } from '@/utils/files'

const props = defineProps({
  task: { type: Object, required: true },
  canSubmit: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  busyBrief: { type: Boolean, default: false },
  lockedReason: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'download-brief'])

const MAX_BYTES = computed(() => (props.task.max_upload_mb ?? 10) * 1024 * 1024)
const input = ref(null)
const picked = ref(null)
const dragging = ref(false)

const accepted = computed(() => props.task.accepted ?? [])

function accepts(name) {
  const lowered = (name ?? '').toLowerCase()
  return accepted.value.some((suffix) => lowered.endsWith(suffix))
}

const problem = computed(() => {
  const file = picked.value
  if (!file) return ''
  if (!accepts(file.name)) return `Use one of these types: ${accepted.value.join(', ')}.`
  if (!file.size) return 'That file is empty.'
  if (file.size > MAX_BYTES.value) return `${file.name} is ${formatBytes(file.size)} — the limit is ${formatBytes(MAX_BYTES.value)}.`
  return ''
})

const valid = computed(() => Boolean(picked.value) && !problem.value)

const hint = computed(() => {
  if (!props.canSubmit) return props.lockedReason || 'MCQs must be answered to enable final verify.'
  if (!picked.value) return 'Pick a file to submit your practical solution.'
  if (problem.value) return problem.value
  return 'Ready — your solution is attached and gets graded on submit.'
})

function choose(next) {
  if (!next || props.submitting) return
  picked.value = next
}

function onPicked(event) {
  const chosen = event.target.files?.[0]
  event.target.value = ''
  choose(chosen ?? null)
}

function onDrop(event) {
  dragging.value = false
  const files = event.dataTransfer?.files
  if (files?.length) choose(files[0])
}

function clear() {
  if (props.submitting) return
  picked.value = null
}

function send() {
  if (!valid.value || !props.canSubmit || props.submitting) return
  emit('submit', picked.value)
}

watch(() => props.task.title, () => { picked.value = null })
</script>

<template>
  <section class="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 shadow-sm sm:p-5">
    <h3 class="text-sm font-extrabold">{{ task.title }}</h3>

    <div class="mt-3 rounded-xl bg-[var(--bg-base)] p-4">
      <p class="text-sm leading-relaxed text-[var(--text-primary)]">{{ task.brief }}</p>
      <ul v-if="task.requirements?.length" class="mt-3 space-y-1.5">
        <li v-for="item in task.requirements" :key="item" class="flex gap-2 text-xs text-[var(--text-secondary)]">
          <span class="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--accent-primary)]"></span>
          <span>{{ item }}</span>
        </li>
      </ul>

      <button
        type="button"
        class="mt-3 inline-flex items-center gap-2 rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] px-3 py-1.5 text-xs font-bold text-[var(--accent-primary)] transition hover:bg-[var(--accent-primary)]/10 disabled:opacity-60"
        :disabled="busyBrief"
        @click="emit('download-brief')"
      >
        <svg v-if="busyBrief" class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.216-8.56"/></svg>
        <svg v-else class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>
        Download task details: {{ task.brief_filename }}
      </button>
    </div>

    <div
      class="mt-4 rounded-xl border-2 border-dashed p-4 transition"
      :class="dragging
        ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10'
        : problem
          ? 'border-[var(--danger-text)] bg-[var(--danger-bg)]'
          : 'border-[var(--accent-primary)]/50 bg-[var(--accent-primary)]/5'"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <p class="text-center text-sm font-extrabold">Upload Completed Script &amp; Outputs</p>

      <div v-if="picked" class="mt-3 flex items-start gap-3 rounded-lg border p-3" :class="problem ? 'border-[var(--danger-border)] bg-[var(--bg-surface)]' : 'border-[var(--success-text)]/40 bg-[var(--success-bg)]'">
        <svg class="mt-0.5 h-4 w-4 shrink-0" :class="problem ? 'text-[var(--danger-text)]' : 'text-[var(--success-text)]'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
        <div class="min-w-0 flex-1">
          <p class="truncate text-xs font-bold">{{ picked.name }} ({{ formatBytes(picked.size) }}) — {{ problem ? 'Needs attention' : 'Ready to upload' }}</p>
          <p v-if="problem" class="mt-1 text-[11px] font-semibold text-[var(--danger-text)]">{{ problem }}</p>
          <p v-else class="mt-1 flex items-center gap-1 text-[11px] font-bold text-[var(--success-text)]">
            <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            File validated
          </p>
        </div>
        <button type="button" class="shrink-0 rounded p-1 text-[var(--text-secondary)] transition hover:text-[var(--danger-text)]" title="Remove file" :disabled="submitting" @click="clear">
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>

      <div v-else-if="task.submission" class="mt-3 flex items-start gap-3 rounded-lg border border-[var(--success-text)]/40 bg-[var(--success-bg)] p-3">
        <svg class="mt-0.5 h-4 w-4 shrink-0 text-[var(--success-text)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
        <div class="min-w-0 flex-1">
          <p class="truncate text-xs font-bold">{{ task.submission.filename }} ({{ formatBytes(task.submission.size) }}) — filed with your result</p>
          <p class="mt-1 flex items-center gap-1 text-[11px] font-bold text-[var(--success-text)]">
            <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            Submitted
          </p>
        </div>
      </div>

      <button type="button" class="mt-3 w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] transition hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] disabled:opacity-60" :disabled="submitting || Boolean(task.submission)" @click="input?.click()">
        Or drop file, script, or zip archive (Max {{ task.max_upload_mb }}MB) here
      </button>
      <input ref="input" type="file" class="hidden" :accept="accepted.join(',')" @change="onPicked" />

      <div v-if="submitting" class="mt-3 h-1 w-full overflow-hidden rounded-full bg-[var(--border-color)]">
        <div class="h-full w-1/3 animate-pulse rounded-full bg-[var(--accent-primary)]"></div>
      </div>
    </div>

    <button
      type="button"
      class="relative mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--accent-primary)] px-4 py-2.5 text-xs font-bold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
      :class="canSubmit && valid ? '' : 'bg-[var(--text-secondary)]/70 hover:bg-[var(--text-secondary)]/70'"
      :disabled="!canSubmit || !valid || submitting"
      @click="send"
    >
      <svg v-if="submitting" class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.216-8.56"/></svg>
      <svg v-else-if="!canSubmit" class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      Submit Practical Solution
    </button>
    <p class="mt-2 text-center text-[11px] text-[var(--text-secondary)]">{{ hint }}</p>
  </section>
</template>
