<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { extractApiError } from '@/api/client'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()

onMounted(async () => {
  if (!auth.user) {
    try {
      await auth.loadProfile()
    } catch (err) {
      auth.logout()
      router.push({ name: 'auth' })
      console.error(extractApiError(err))
    }
  }
})

function handleLogout() {
  auth.logout()
  router.push({ name: 'auth' })
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <header class="border-b border-slate-800 bg-slate-900/60">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 font-bold">⇄</div>
          <span class="text-lg font-semibold">Skill Swap</span>
        </div>
        <button
          type="button"
          class="rounded-lg border border-slate-700 px-4 py-1.5 text-sm font-medium text-slate-300 transition hover:border-red-500/50 hover:text-red-400"
          @click="handleLogout"
        >
          Log out
        </button>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-10">
      <template v-if="auth.user">
        <h1 class="text-3xl font-bold">Hi, {{ auth.user.full_name }} 👋</h1>
        <p class="mt-1 text-slate-400">{{ auth.user.email }}</p>
        <p v-if="auth.user.designation" class="mt-1 text-sm text-indigo-400">{{ auth.user.designation }}</p>
        <p v-if="auth.user.bio" class="mt-4 max-w-2xl text-slate-300">{{ auth.user.bio }}</p>

        <section class="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 class="text-lg font-semibold">Your skills</h2>
          <p v-if="!auth.user.skills?.length" class="mt-2 text-sm text-slate-400">
            No skills yet — add them to start getting matches.
          </p>
          <div v-else class="mt-3 flex flex-wrap gap-2">
            <span
              v-for="skill in auth.user.skills"
              :key="skill.id"
              class="rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-300"
            >
              {{ skill.skill_type }} · {{ skill.proficiency }}
            </span>
          </div>
        </section>
      </template>
      <p v-else class="text-slate-400">Loading your profile…</p>
    </main>
  </div>
</template>
