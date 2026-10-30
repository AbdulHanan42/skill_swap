<script setup>
defineProps({
  tabs: { type: Array, required: true }, // [{ key, label, count }]
  modelValue: { type: String, required: true },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="-mb-px flex gap-1 overflow-x-auto border-b border-[var(--border-color)]" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      role="tab"
      class="flex shrink-0 items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-semibold transition"
      :class="tab.key === modelValue
        ? 'border-[var(--accent-primary)] text-[var(--accent-primary)]'
        : 'border-transparent text-[var(--text-secondary)] hover:border-[var(--border-color)] hover:text-[var(--text-primary)]'"
      :aria-selected="tab.key === modelValue"
      @click="emit('update:modelValue', tab.key)"
    >
      {{ tab.label }} ({{ tab.count }})
    </button>
  </div>
</template>
