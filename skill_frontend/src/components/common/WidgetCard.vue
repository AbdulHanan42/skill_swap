<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
    <div class="mb-4 flex items-start justify-between gap-3">
      <div class="min-w-0">
        <h2 class="truncate text-base font-bold">{{ title }}</h2>
        <p v-if="subtitle" class="mt-0.5 text-xs text-[var(--text-secondary)]">{{ subtitle }}</p>
      </div>
      <slot name="actions" />
    </div>
    <slot />
  </section>
</template>
