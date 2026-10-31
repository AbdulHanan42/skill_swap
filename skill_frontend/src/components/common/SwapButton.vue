<script setup>
import { computed } from 'vue'

const props = defineProps({
  // available | sending | requested_by_me | requested_by_them | connected
  state: { type: String, default: 'available' },
  size: { type: String, default: 'md' }, // sm | md
  emoji: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const LOCKED = ['sending', 'requested_by_me', 'connected']

const LABELS = {
  sending: 'Sending…',
  requested_by_me: 'Request Sent',
  requested_by_them: 'Respond',
  connected: 'Connected',
}

const label = computed(
  () => LABELS[props.state] ?? (props.emoji ? '🤝 Request Swap' : 'Request Swap'),
)

const tone = computed(() => {
  if (props.state === 'requested_by_them') {
    return 'border border-[var(--warning-text)]/50 bg-[var(--warning-bg)] text-[var(--warning-text)]'
  }
  if (props.state === 'connected') {
    return 'border border-[var(--success-text)]/50 bg-[var(--success-bg)] text-[var(--success-text)]'
  }
  if (props.state === 'requested_by_me') {
    return 'border border-[var(--border-color)] bg-[var(--bg-base)] text-[var(--text-secondary)]'
  }
  return 'bg-[var(--accent-primary)] text-white hover:bg-[var(--accent-hover)] disabled:opacity-60'
})

function onClick() {
  if (LOCKED.includes(props.state)) return
  emit('click', props.state)
}
</script>

<template>
  <button
    type="button"
    :disabled="LOCKED.includes(state)"
    class="inline-flex items-center justify-center gap-1.5 rounded-lg font-semibold transition disabled:cursor-not-allowed"
    :class="[size === 'md' ? 'px-4 py-2.5 text-sm' : 'px-3 py-2 text-xs', tone]"
    @click="onClick"
  >
    <svg v-if="state === 'sending'" :class="size === 'md' ? 'h-4 w-4' : 'h-3.5 w-3.5'" class="animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25" /><path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="4" stroke-linecap="round" /></svg>
    <svg v-else-if="state === 'requested_by_me'" :class="size === 'md' ? 'h-4 w-4' : 'h-3.5 w-3.5'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
    <svg v-else-if="state === 'requested_by_them'" :class="size === 'md' ? 'h-4 w-4' : 'h-3.5 w-3.5'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
    <svg v-else-if="state === 'connected'" :class="size === 'md' ? 'h-4 w-4' : 'h-3.5 w-3.5'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12H7.5a2.5 2.5 0 0 1 0-5H9"/><path d="M15 7h1.5a2.5 2.5 0 0 1 0 5H15"/><path d="M8 9.5h8"/></svg>
    {{ label }}
  </button>
</template>
