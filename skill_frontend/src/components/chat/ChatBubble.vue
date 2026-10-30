<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: Object, required: true },
  mine: { type: Boolean, required: true },
})

const time = computed(() =>
  new Date(props.message.sent_at).toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  }),
)
</script>

<template>
  <div class="flex" :class="mine ? 'justify-end' : 'justify-start'">
    <div class="max-w-[85%] sm:max-w-[70%]">
      <div
        class="rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm"
        :class="mine
          ? 'rounded-br-md bg-[var(--accent-primary)] text-white'
          : 'rounded-bl-md border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)]'"
      >{{ message.content }}</div>
      <p class="mt-1 px-1 text-[10px] text-[var(--text-secondary)]" :class="mine ? 'text-right' : 'text-left'">{{ time }}</p>
    </div>
  </div>
</template>
