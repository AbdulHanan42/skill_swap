<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  src: { type: String, default: null },
  size: { type: String, default: 'md' }, // sm | header | md | lg
})

const SIZES = {
  sm: 'h-8 w-8 text-[11px]',
  header: 'h-10 w-10 text-sm',
  md: 'h-12 w-12 text-lg',
  lg: 'h-16 w-16 text-xl',
}

const classes = computed(() => SIZES[props.size] ?? SIZES.md)
const initial = computed(() => (props.name.trim().charAt(0) || '?').toUpperCase())
</script>

<template>
  <img v-if="src" :src="src" :alt="name" class="shrink-0 rounded-full object-cover" :class="classes" />
  <div
    v-else
    class="flex shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] font-bold text-white"
    :class="classes"
  >{{ initial }}</div>
</template>
