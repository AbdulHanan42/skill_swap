<script setup>
import ScoreRing from '@/components/common/ScoreRing.vue'
import SkillTag from '@/components/common/SkillTag.vue'
import SwapButton from '@/components/common/SwapButton.vue'

defineProps({
  match: { type: Object, required: true }, // { user_id, name, designation, avatar, score, offers[], wants[] }
  state: { type: String, default: 'available' },
})

defineEmits(['request-swap', 'view-profile'])
</script>

<template>
  <section class="relative mt-6 rounded-xl border border-[var(--accent-primary)]/40 bg-[var(--bg-surface)] p-5 shadow-sm" style="box-shadow: 0 0 24px -8px color-mix(in srgb, var(--accent-primary) 35%, transparent)">
    <span class="absolute -top-2.5 left-5 rounded-full bg-[var(--accent-primary)] px-3 py-0.5 text-[11px] font-bold text-white">✨ Top AI Match</span>
    <div class="flex flex-wrap items-center gap-5 pt-2">
      <img v-if="match.avatar" :src="match.avatar" :alt="match.name" class="h-16 w-16 shrink-0 rounded-full object-cover" />
      <div v-else class="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-xl font-bold text-white">{{ match.name.charAt(0).toUpperCase() }}</div>
      <div class="min-w-0 flex-1">
        <h3 class="text-lg font-bold">{{ match.name }}</h3>
        <p class="text-sm text-[var(--text-secondary)]">{{ match.designation }}</p>
        <div class="mt-3 flex flex-wrap gap-x-8 gap-y-2">
          <div>
            <p class="text-[11px] font-semibold text-[var(--text-secondary)]">They Can Teach You (Offers):</p>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <SkillTag v-for="skill in match.offers" :key="skill" :label="skill" variant="offer" />
              <span v-if="!match.offers.length" class="text-[11px] italic text-[var(--text-secondary)]">—</span>
            </div>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-[var(--text-secondary)]">They Want to Learn (Wants):</p>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <SkillTag v-for="skill in match.wants" :key="skill" :label="skill" variant="want" />
              <span v-if="!match.wants.length" class="text-[11px] italic text-[var(--text-secondary)]">—</span>
            </div>
          </div>
        </div>
      </div>
      <ScoreRing :score="match.score" :size="80" />
      <div class="flex shrink-0 gap-2">
        <button type="button" class="rounded-lg border border-[var(--border-color)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--bg-base)]" @click="$emit('view-profile')">View Profile</button>
        <SwapButton size="md" emoji :state="state" @click="$emit('request-swap')" />
      </div>
    </div>
  </section>
</template>
