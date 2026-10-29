<template>
  <div class="flex flex-col gap-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm md:flex-row md:items-center md:justify-between">
    <div class="flex flex-1 items-center gap-4">
      <div class="h-16 w-16 shrink-0 animate-pulse rounded-full bg-[var(--bg-base)]"></div>
      <div class="min-w-0 flex-1 space-y-2">
        <div class="h-4 w-40 animate-pulse rounded bg-[var(--bg-base)]"></div>
        <div class="h-3 w-28 animate-pulse rounded bg-[var(--bg-base)]"></div>
        <div class="mt-3 flex gap-2">
          <div class="h-6 w-20 animate-pulse rounded-lg bg-[var(--bg-base)]"></div>
          <div class="h-6 w-24 animate-pulse rounded-lg bg-[var(--bg-base)]"></div>
        </div>
      </div>
    </div>
    <div class="h-[78px] w-[78px] shrink-0 animate-pulse rounded-full bg-[var(--bg-base)]"></div>
    <div class="w-full space-y-2 md:w-40">
      <div class="h-9 animate-pulse rounded-lg bg-[var(--bg-base)]"></div>
      <div class="h-9 animate-pulse rounded-lg bg-[var(--bg-base)]"></div>
    </div>
  </div>
</template>
