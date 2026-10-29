<script setup>
defineProps({
  title: { type: String, required: true },
  message: { type: String, default: '' },
})
</script>

<template>
  <div class="flex flex-col items-center rounded-xl border border-dashed border-[var(--border-color)] bg-[var(--bg-surface)] px-6 py-14 text-center shadow-sm">
    <div class="flex h-14 w-14 items-center justify-center rounded-full bg-[var(--accent-primary)]/10">
      <slot name="icon">
        <svg class="h-7 w-7 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3 4 7l4 4" /><path d="M4 7h16" /><path d="m16 21 4-4-4-4" /><path d="M20 17H4" /></svg>
      </slot>
    </div>
    <h3 class="mt-4 text-base font-bold">{{ title }}</h3>
    <p v-if="message" class="mt-1 max-w-sm text-sm text-[var(--text-secondary)]">{{ message }}</p>
    <slot />
  </div>
</template>
