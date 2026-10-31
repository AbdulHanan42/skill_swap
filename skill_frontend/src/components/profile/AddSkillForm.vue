<script setup>
import { ref } from 'vue'

const props = defineProps({
  isAdding: { type: Boolean, default: false },
  levels: { type: Array, default: () => ['Beginner', 'Intermediate', 'Expert'] },
  initialProficiency: { type: String, default: 'Beginner' },
})

const emit = defineEmits(['add'])

const name = ref('')
const skillType = ref('OFFERS')
const proficiency = ref(props.initialProficiency)

function submit() {
  const trimmed = name.value.trim()
  if (!trimmed) return
  emit('add', { skillName: trimmed, skillType: skillType.value, proficiency: proficiency.value })
  name.value = ''
}
</script>

<template>
  <div class="mt-5 grid grid-cols-1 gap-2 sm:grid-cols-[1fr_auto_auto_auto]">
    <input
      v-model="name"
      type="text"
      placeholder="Skill name (e.g. Vue.js)"
      class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]"
      @keyup.enter="submit"
    />
    <select v-model="skillType" class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]">
      <option value="OFFERS">Offers</option>
      <option value="WANTS">Wants</option>
    </select>
    <select v-model="proficiency" class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]">
      <option v-for="level in props.levels" :key="level" :value="level">{{ level }}</option>
    </select>
    <button
      type="button"
      :disabled="props.isAdding"
      class="rounded-lg bg-[var(--accent-primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
      @click="submit"
    >
      {{ props.isAdding ? 'Adding…' : '+ Add' }}
    </button>
  </div>
</template>
