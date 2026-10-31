<script setup>
const props = defineProps({
  label: { type: String, required: true },
  variant: { type: String, default: 'offer' }, // offer | want
  size: { type: String, default: 'sm' }, // sm | md
  removable: { type: Boolean, default: false },
})

defineEmits(['remove'])
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 font-semibold"
    :class="[
      props.variant === 'want'
        ? 'bg-[var(--warning-bg)] text-[var(--warning-text)]'
        : 'bg-[var(--success-bg)] text-[var(--success-text)]',
      props.size === 'md' ? 'rounded-lg px-2.5 py-1 text-xs' : 'rounded-md px-2 py-0.5 text-[11px]',
    ]"
  >{{ props.label }}<button
    v-if="props.removable"
    type="button"
    aria-label="Remove skill"
    class="opacity-60 transition hover:opacity-100"
    @click="$emit('remove')"
  >&times;</button></span>
</template>
