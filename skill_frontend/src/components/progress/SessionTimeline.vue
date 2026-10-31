<script setup>
import { formatDay, formatHours } from '@/utils/time'

defineProps({
  sessions: { type: Array, required: true }, // [{ id, subject, peer_name, completed_at, hours }]
})
</script>

<template>
  <ol v-if="sessions.length" class="relative space-y-5 pl-6">
    <span class="absolute left-[7px] top-2 bottom-2 w-px bg-[var(--border-color)]" aria-hidden="true" />
    <li v-for="session in sessions" :key="session.id" class="relative">
      <span class="absolute -left-6 top-1 flex h-[15px] w-[15px] items-center justify-center rounded-full border-2 border-[var(--accent-primary)] bg-[var(--bg-surface)]">
        <span class="h-1.5 w-1.5 rounded-full bg-[var(--accent-primary)]" />
      </span>
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <p class="truncate text-sm font-bold">{{ session.subject }} <span class="font-medium text-[var(--text-secondary)]">with {{ session.peer_name }}</span></p>
          <p class="mt-0.5 text-xs text-[var(--text-secondary)]">
            {{ formatDay(session.completed_at) }}<span class="mx-1 opacity-40">·</span>{{ formatHours(session.hours) }}
          </p>
        </div>
        <span class="shrink-0 rounded-md bg-[var(--success-bg)] px-2 py-0.5 text-[11px] font-bold text-[var(--success-text)]">Completed</span>
      </div>
    </li>
  </ol>
  <p v-else class="rounded-lg border border-dashed border-[var(--border-color)] px-4 py-8 text-center text-sm text-[var(--text-secondary)]">
    No completed swaps yet.
    <RouterLink :to="{ name: 'skill-matching' }" class="font-semibold text-[var(--accent-primary)] hover:underline">Find a skill twin</RouterLink>
    and log your first session.
  </p>
</template>
