<script setup>
const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  hint: { type: String, default: '' },
  chip: { type: String, default: '' },
  chipTone: { type: String, default: 'success' }, // success | warning | accent
  valueTone: { type: String, default: 'default' }, // default | accent
})

const CHIP_TONES = {
  success: 'bg-[var(--success-bg)] text-[var(--success-text)]',
  warning: 'bg-[var(--warning-bg)] text-[var(--warning-text)]',
  danger: 'bg-[var(--danger-bg)] text-[var(--danger-text)]',
  accent: 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]',
}

const VALUE_TONES = {
  default: 'text-[var(--text-primary)]',
  accent: 'text-[var(--accent-primary)]',
}
</script>

<template>
  <div class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 shadow-sm transition hover:shadow-md">
    <div class="flex items-start justify-between gap-2">
      <p class="text-sm font-semibold text-[var(--text-secondary)]">{{ label }}</p>
      <span
        v-if="chip"
        class="rounded-md px-2 py-0.5 text-[11px] font-bold"
        :class="CHIP_TONES[props.chipTone] ?? CHIP_TONES.success"
      >{{ chip }}</span>
      <slot v-else name="icon" />
    </div>
    <p class="mt-2 flex items-baseline gap-1.5">
      <span class="text-3xl font-extrabold leading-none" :class="VALUE_TONES[props.valueTone] ?? VALUE_TONES.default">{{ value }}</span>
      <span v-if="unit" class="text-base font-bold" :class="VALUE_TONES[props.valueTone] ?? VALUE_TONES.default">{{ unit }}</span>
      <span v-if="hint" class="text-xs font-medium text-[var(--text-secondary)]">{{ hint }}</span>
    </p>
  </div>
</template>
