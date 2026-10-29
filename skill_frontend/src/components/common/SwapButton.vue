<script setup>
const props = defineProps({
  sent: { type: Boolean, default: false },
  pending: { type: Boolean, default: false },
  size: { type: String, default: 'md' }, // sm | md
  emoji: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

function onClick() {
  if (props.sent || props.pending) return
  emit('click')
}
</script>

<template>
  <button
    type="button"
    :disabled="props.sent || props.pending"
    class="inline-flex items-center justify-center gap-1.5 rounded-lg bg-[var(--accent-primary)] font-semibold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
    :class="props.size === 'md' ? 'px-4 py-2.5 text-sm' : 'px-3 py-2 text-xs'"
    @click="onClick"
  >
    <svg v-if="props.pending" :class="props.size === 'md' ? 'h-4 w-4' : 'h-3.5 w-3.5'" class="animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25" /><path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="4" stroke-linecap="round" /></svg>
    <svg v-else-if="props.sent" :class="props.size === 'md' ? 'h-4 w-4' : 'h-3.5 w-3.5'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
    {{ props.pending ? 'Sending…' : props.sent ? 'Request Sent' : `${props.emoji ? '🤝 ' : ''}Request Swap` }}
  </button>
</template>
