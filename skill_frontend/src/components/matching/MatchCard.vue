<script setup>
import SkillTag from '@/components/common/SkillTag.vue'
import SwapButton from '@/components/common/SwapButton.vue'

defineProps({
  match: { type: Object, required: true }, // { user_id, name, designation, avatar, score, offers[], wants[] }
  sent: { type: Boolean, default: false },
  pending: { type: Boolean, default: false },
})

defineEmits(['request-swap', 'view-profile'])
</script>

<template>
  <div class="flex flex-col rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm transition-all hover:shadow-md">
    <div class="flex items-center gap-3">
      <img v-if="match.avatar" :src="match.avatar" :alt="match.name" class="h-11 w-11 shrink-0 rounded-full object-cover" />
      <div v-else class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-base font-bold text-white">{{ match.name.charAt(0).toUpperCase() }}</div>
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-bold">{{ match.name }}</p>
        <p class="truncate text-xs text-[var(--text-secondary)]">{{ match.designation }}</p>
      </div>
      <span class="shrink-0 rounded-full bg-[var(--bg-base)] px-2.5 py-1 text-[11px] font-bold text-[var(--accent-primary)]">{{ match.score }}% Match</span>
    </div>
    <div class="mt-4 space-y-2.5">
      <div class="flex flex-wrap items-center gap-1.5">
        <span class="text-[11px] font-semibold text-[var(--text-secondary)]">They Teach:</span>
        <SkillTag v-for="skill in match.offers" :key="skill" :label="skill" variant="offer" />
      </div>
      <div class="flex flex-wrap items-center gap-1.5">
        <span class="text-[11px] font-semibold text-[var(--text-secondary)]">They Want:</span>
        <SkillTag v-for="skill in match.wants" :key="skill" :label="skill" variant="want" />
      </div>
    </div>
    <div class="mt-auto grid grid-cols-2 gap-2 pt-5">
      <button type="button" class="rounded-lg border border-[var(--border-color)] px-3 py-2 text-xs font-semibold text-[var(--text-primary)] transition hover:bg-[var(--bg-base)]" @click="$emit('view-profile')">View Profile</button>
      <SwapButton size="sm" :sent="sent" :pending="pending" @click="$emit('request-swap')" />
    </div>
  </div>
</template>
