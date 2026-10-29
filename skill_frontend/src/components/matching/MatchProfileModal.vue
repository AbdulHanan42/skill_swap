<script setup>
import SkillTag from '@/components/common/SkillTag.vue'
import SwapButton from '@/components/common/SwapButton.vue'

defineProps({
  match: { type: Object, default: null }, // { name, designation, avatar, bio, score, offers[], wants[] }
  sent: { type: Boolean, default: false },
  pending: { type: Boolean, default: false },
})

defineEmits(['close', 'request-swap'])
</script>

<template>
  <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0" leave-active-class="transition duration-200" leave-to-class="opacity-0">
    <div v-if="match" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" @click.self="$emit('close')">
      <div class="w-full max-w-md rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-6 shadow-xl">
        <div class="flex items-start gap-4">
          <img v-if="match.avatar" :src="match.avatar" :alt="match.name" class="h-16 w-16 rounded-full object-cover" />
          <div v-else class="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--accent-primary)] text-xl font-bold text-white">{{ match.name.charAt(0).toUpperCase() }}</div>
          <div class="min-w-0 flex-1">
            <h3 class="text-lg font-bold">{{ match.name }}</h3>
            <p class="text-sm text-[var(--text-secondary)]">{{ match.designation }}</p>
            <p class="mt-1 text-xs font-semibold text-[var(--accent-primary)]">{{ match.score }}% match with your portfolio</p>
          </div>
          <button type="button" aria-label="Close" class="text-xl text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]" @click="$emit('close')">&times;</button>
        </div>
        <p v-if="match.bio" class="mt-4 rounded-lg bg-[var(--bg-base)]/60 p-3 text-sm text-[var(--text-secondary)]">{{ match.bio }}</p>
        <p class="mt-4 text-xs font-semibold">They Teach</p>
        <div class="mt-1.5 flex flex-wrap gap-1.5">
          <SkillTag v-for="skill in match.offers" :key="skill" :label="skill" variant="offer" />
          <span v-if="!match.offers.length" class="text-[11px] italic text-[var(--text-secondary)]">No offers listed</span>
        </div>
        <p class="mt-3 text-xs font-semibold">They Want</p>
        <div class="mt-1.5 flex flex-wrap gap-1.5">
          <SkillTag v-for="skill in match.wants" :key="skill" :label="skill" variant="want" />
          <span v-if="!match.wants.length" class="text-[11px] italic text-[var(--text-secondary)]">No wants listed</span>
        </div>
        <SwapButton class="mt-6 w-full" size="md" :sent="sent" :pending="pending" @click="$emit('request-swap')" />
      </div>
    </div>
  </Transition>
</template>
