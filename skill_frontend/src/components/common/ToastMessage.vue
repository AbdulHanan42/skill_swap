<script setup>
import { watch } from 'vue'

const props = defineProps({
  message: { type: String, required: true },
  type: { type: String, default: 'success' }, // success | error
  duration: { type: Number, default: 3500 },
})

const emit = defineEmits(['dismiss'])

let timer = null
watch(
  () => props.message,
  (msg) => {
    clearTimeout(timer)
    if (msg) timer = setTimeout(() => emit('dismiss'), props.duration)
  },
  { immediate: true },
)
</script>

<template>
  <Transition enter-active-class="transition duration-300" enter-from-class="opacity-0 translate-y-2" leave-active-class="transition duration-300" leave-to-class="opacity-0">
    <p
      v-if="message"
      class="flex items-center gap-2 rounded-lg border px-4 py-2.5 text-xs font-semibold"
      :class="type === 'error'
        ? 'border-[var(--danger-border)] bg-[var(--danger-bg)] text-[var(--danger-text)]'
        : 'border-[var(--success-bg)] bg-[var(--success-bg)] text-[var(--success-text)]'"
    ><svg v-if="type !== 'error'" class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>{{ message }}</p>
  </Transition>
</template>
