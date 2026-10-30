<script setup>
import { computed } from 'vue'

import ScoreRing from '@/components/common/ScoreRing.vue'
import SkillTag from '@/components/common/SkillTag.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatRelative } from '@/utils/time'

const props = defineProps({
  request: { type: Object, required: true },
  direction: { type: String, default: 'incoming' }, // incoming | sent
  acting: { type: Boolean, default: false },
  accepted: { type: Boolean, default: false },
  fading: { type: Boolean, default: false },
})

defineEmits(['accept', 'decline'])

const score = () => Math.round(props.request.match_score ?? 0)

const waitingFor = computed(() => `Waiting for ${props.request.peer_name.split(' ')[0]}`)
</script>

<template>
  <article
    class="flex flex-col gap-4 rounded-xl border bg-[var(--bg-surface)] p-5 shadow-sm transition-all duration-300 hover:shadow-md md:flex-row md:items-center md:justify-between"
    :class="[
      fading ? 'translate-x-6 opacity-0' : 'translate-x-0 opacity-100',
      accepted
        ? 'border-[var(--success-text)]/50'
        : 'border-[var(--border-color)]',
    ]"
  >
    <div class="flex min-w-0 flex-1 flex-col gap-4 sm:flex-row sm:items-center">
      <UserAvatar :name="request.peer_name" :src="request.peer_avatar" size="lg" />

      <div class="min-w-0">
        <h3 class="text-base font-bold">{{ request.peer_name }}</h3>
        <p class="text-xs text-[var(--text-secondary)]">
          {{ request.peer_designation || 'Skill swapper' }}
          <span class="mx-1 opacity-40">·</span>
          {{ direction === 'sent' ? 'sent' : 'received' }} {{ formatRelative(request.requested_at) }}
        </p>

        <div class="mt-3 flex flex-wrap gap-x-6 gap-y-3">
          <div class="min-w-0">
            <p class="text-[11px] font-semibold text-[var(--text-secondary)]">They Can Teach You (Offers):</p>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <SkillTag v-for="skill in request.offers" :key="skill" :label="skill" variant="offer" size="md" />
              <span v-if="!request.offers.length" class="text-xs italic text-[var(--text-secondary)]">Nothing listed yet</span>
            </div>
          </div>

          <div class="min-w-0">
            <p class="text-[11px] font-semibold text-[var(--text-secondary)]">They Want to Learn (Wants):</p>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <SkillTag v-for="skill in request.wants" :key="skill" :label="skill" variant="want" size="md" />
              <span v-if="!request.wants.length" class="text-xs italic text-[var(--text-secondary)]">Nothing listed yet</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ScoreRing class="shrink-0 self-center" :score="score()" :size="78" label="Match Score" />

    <div class="flex shrink-0 flex-col gap-2 sm:flex-row md:w-40 md:flex-col">
      <template v-if="direction === 'incoming' && !accepted">
        <button
          type="button"
          class="flex items-center justify-center gap-2 rounded-lg bg-[var(--accent-primary)] px-4 py-2 text-sm font-bold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="acting || fading"
          @click="$emit('accept', request)"
        >
          <svg v-if="acting" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.2-8.6" /></svg>
          <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
          {{ acting ? 'Accepting…' : 'Accept Swap' }}
        </button>
        <button
          type="button"
          class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-4 py-2 text-sm font-semibold text-[var(--text-secondary)] transition hover:border-[var(--danger-border)] hover:bg-[var(--danger-bg)] hover:text-[var(--danger-text)] disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="acting || fading"
          @click="$emit('decline', request)"
        >Decline</button>
      </template>

      <span v-else-if="accepted" class="flex items-center justify-center gap-2 rounded-lg border border-[var(--success-text)]/40 bg-[var(--success-bg)] px-4 py-2 text-sm font-bold text-[var(--success-text)]">
        <svg class="h-4 w-4 shrink-0 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.2-8.6" /></svg>
        Accepted
      </span>

      <span v-else class="flex items-center justify-center gap-2 rounded-lg border border-[var(--warning-text)]/40 bg-[var(--warning-bg)] px-4 py-2 text-center text-sm font-semibold text-[var(--warning-text)]">
        <span class="relative flex h-2 w-2 shrink-0">
          <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--warning-text)] opacity-60"></span>
          <span class="relative inline-flex h-2 w-2 rounded-full bg-[var(--warning-text)]"></span>
        </span>
        {{ waitingFor }}
      </span>
    </div>
  </article>
</template>
