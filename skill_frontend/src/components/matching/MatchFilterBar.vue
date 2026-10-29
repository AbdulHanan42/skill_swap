<script setup>
const props = defineProps({
  search: { type: String, default: '' },
  sort: { type: String, default: 'highest' },
  level: { type: String, default: 'all' },
  levels: { type: Array, default: () => ['all', 'Beginner', 'Intermediate', 'Expert'] },
})

defineEmits(['update:search', 'update:sort', 'update:level'])
</script>

<template>
  <div class="flex flex-wrap items-center gap-3 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 shadow-sm">
    <div class="relative min-w-0 flex-1">
      <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /></svg>
      <input
        :value="props.search"
        type="search"
        placeholder="Search skills or name..."
        class="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] py-2.5 pl-9 pr-3 text-sm outline-none transition focus:border-[var(--accent-primary)]"
        @input="$emit('update:search', $event.target.value)"
      />
    </div>
    <select
      :value="props.sort"
      class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]"
      @change="$emit('update:sort', $event.target.value)"
    >
      <option value="highest">Match Percentage: Highest first</option>
      <option value="lowest">Match Percentage: Lowest first</option>
    </select>
    <select
      :value="props.level"
      class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]"
      @change="$emit('update:level', $event.target.value)"
    >
      <option v-for="level in props.levels" :key="level" :value="level">{{ level === 'all' ? 'Experience Level: All' : level }}</option>
    </select>
  </div>
</template>
