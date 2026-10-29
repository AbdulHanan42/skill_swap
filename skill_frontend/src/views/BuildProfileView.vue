<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { extractApiError } from '@/api/client'
import { addSkill, getDashboardOverview, listSkillCatalog, updateProfile } from '@/api/profileApi'
import AppLayout from '@/components/common/AppLayout.vue'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const router = useRouter()

/* ---------- form state (prefilled from GET /profile/me) ---------- */

const fullName = ref('')
const designation = ref('')
const bio = ref('')

const avatarUrl = ref('')
const avatarInput = ref(null)

const skills = ref([]) // { id, skill_id, skill_type, proficiency, name }

const newSkillName = ref('')
const newSkillType = ref('OFFERS')
const newSkillProficiency = ref('Beginner')

const completeness = ref(0)

const isLoading = ref(false)
const isAdding = ref(false)
const error = ref('')
const notice = ref('')

const experienceLevels = ['Beginner', 'Intermediate', 'Expert']

const suggestions = ['Python', 'SQL', 'Figma', 'Docker', 'UI Design', 'UX']

const offers = computed(() => skills.value.filter((s) => s.skill_type === 'OFFERS'))
const wants = computed(() => skills.value.filter((s) => s.skill_type === 'WANTS'))

const userInitial = computed(() => (fullName.value || auth.user?.full_name || 'U').trim().charAt(0).toUpperCase())

/* ---------- load profile + catalog on mount ---------- */

onMounted(async () => {
  try {
    const [profile, catalog] = await Promise.all([
      auth.user ? Promise.resolve(auth.user) : auth.loadProfile(),
      listSkillCatalog().catch(() => []),
    ])
    const nameById = Object.fromEntries(catalog.map((s) => [s.id, s.name]))
    fullName.value = profile.full_name ?? ''
    designation.value = profile.designation ?? ''
    bio.value = profile.bio ?? ''
    skills.value = (profile.skills ?? []).map((s) => ({
      ...s,
      name: nameById[s.skill_id] ?? `Skill #${s.skill_id}`,
    }))
  } catch (err) {
    error.value = extractApiError(err)
  }
  try {
    const overview = await getDashboardOverview()
    completeness.value = Math.round(overview.profile_completeness)
  } catch {
    // decorative only; keep 0% fallback
  }
})

/* ---------- avatar ---------- */

function pickAvatar() {
  avatarInput.value?.click()
}

function onAvatarChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (avatarUrl.value) URL.revokeObjectURL(avatarUrl.value)
  avatarUrl.value = URL.createObjectURL(file)
}

/* ---------- skills ---------- */

async function submitSkill(name) {
  if (isAdding.value) return
  error.value = ''
  notice.value = ''
  const skillName = (name ?? newSkillName.value).trim()
  if (!skillName) {
    error.value = 'Enter a skill name first.'
    return
  }
  isAdding.value = true
  try {
    const result = await addSkill({
      skillName,
      category: null,
      skillType: newSkillType.value,
      proficiency: newSkillProficiency.value,
    })
    const added = result.skill ?? result
    skills.value.push({
      ...added,
      name: skillName,
    })
    if (!name) newSkillName.value = ''
    notice.value = `"${skillName}" added to your portfolio.`
  } catch (err) {
    error.value = extractApiError(err)
  } finally {
    isAdding.value = false
  }
}

function removeSkill(index) {
  const removed = skills.value.splice(index, 1)[0]
  notice.value = `"${removed.name}" removed from this form. Note: the backend has no delete endpoint yet, so it stays saved on your profile until one exists.`
}

/* ---------- save ---------- */

async function saveAndContinue() {
  isLoading.value = true
  error.value = ''
  notice.value = ''
  try {
    const updated = await updateProfile({
      fullName: fullName.value.trim() || undefined,
      designation: designation.value.trim(),
      bio: bio.value.trim(),
    })
    auth.user = updated
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = extractApiError(err)
  } finally {
    isLoading.value = false
  }
}

function previewProfile() {
  router.push({ name: 'dashboard' })
}
</script>

<template>
  <AppLayout>
    <template #header-sub>
      <div class="mt-1 max-w-md">
        <div class="flex items-center justify-between text-xs">
          <span class="font-semibold text-[var(--accent-primary)]">Step 2 of 3: Skill &amp; Experience Details</span>
          <span class="text-[var(--text-secondary)]">66%</span>
        </div>
        <div class="mt-2 h-2 overflow-hidden rounded-full bg-[var(--bg-base)]">
          <div class="h-full w-2/3 rounded-full bg-[var(--accent-primary)] transition-all duration-700" />
        </div>
      </div>
    </template>

    <div class="mx-auto flex w-full max-w-3xl flex-col gap-5 pb-24">
      <!-- messages -->
      <p v-if="error" class="rounded-lg border border-red-300 bg-red-50 px-4 py-2.5 text-xs font-semibold text-red-600">{{ error }}</p>
      <p v-if="notice" class="rounded-lg border border-[var(--accent-primary)]/40 bg-[var(--accent-primary)]/10 px-4 py-2.5 text-xs font-semibold text-[var(--accent-primary)]">{{ notice }}</p>

      <!-- Profile completeness -->
      <section class="flex items-center gap-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <div class="min-w-0 flex-1">
          <h2 class="text-sm font-bold">Profile {{ completeness }}% Complete</h2>
          <p class="mt-1 text-xs text-[var(--text-secondary)]">
            {{ completeness >= 100
              ? 'Your profile is fully filled out. Great work!'
              : 'Fill in the sections below to boost your match ranking and complete your swap profile.' }}
          </p>
          <div class="mt-3 h-2 overflow-hidden rounded-full bg-[var(--bg-base)]">
            <div class="h-full rounded-full bg-[var(--success-text)] transition-all duration-700" :style="{ width: `${completeness}%` }" />
          </div>
        </div>
        <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border-4 border-[var(--accent-primary)]/30 text-lg font-bold text-[var(--accent-primary)]">{{ completeness }}%</div>
      </section>

      <!-- Card 1: Personal Details -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="text-sm font-bold">Personal Details</h2>
        <div class="mt-4 flex items-center gap-4">
          <div class="relative shrink-0">
            <img v-if="avatarUrl" :src="avatarUrl" alt="Avatar preview" class="h-16 w-16 rounded-full object-cover ring-2 ring-[var(--accent-primary)]" />
            <div v-else class="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--accent-primary)] text-xl font-bold text-white">{{ userInitial }}</div>
            <button type="button" @click="pickAvatar" class="absolute -bottom-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-secondary)] transition hover:text-[var(--accent-primary)]" title="Upload avatar">
              <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" /></svg>
            </button>
            <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
          </div>
          <div class="min-w-0">
            <p class="text-xs font-semibold">Profile Photo</p>
            <p class="mt-0.5 text-[11px] text-[var(--text-secondary)]">JPG or PNG, square works best. Shown to your swap partners.</p>
            <button type="button" @click="pickAvatar" class="mt-2 rounded-lg border border-[var(--accent-primary)] px-3 py-1.5 text-xs font-semibold text-[var(--accent-primary)] transition hover:bg-[var(--accent-primary)]/10">Upload Image</button>
          </div>
        </div>

        <label class="mt-5 block">
          <span class="mb-1.5 block text-xs font-semibold">Full Name</span>
          <input v-model="fullName" type="text" placeholder="Your name" class="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]" />
        </label>

        <label class="mt-4 block">
          <span class="mb-1.5 block text-xs font-semibold">Designation / Headline</span>
          <input v-model="designation" type="text" placeholder="e.g. Full Stack Developer" class="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]" />
        </label>

        <label class="mt-4 block">
          <span class="mb-1.5 block text-xs font-semibold">Bio</span>
          <textarea v-model="bio" rows="4" placeholder="Tell other swappers who you are and what you love to teach &amp; learn..." class="w-full resize-none rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]" />
        </label>
      </section>

      <!-- Card 2: Goals & Experience -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="text-sm font-bold">Goals &amp; Experience</h2>
        <label class="mt-4 block">
          <span class="mb-1.5 block text-xs font-semibold">Experience Level</span>
          <select v-model="newSkillProficiency" class="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]">
            <option v-for="level in experienceLevels" :key="level" :value="level">{{ level }}</option>
          </select>
          <p class="mt-1.5 text-[11px] text-[var(--text-secondary)]">Applied to skills you add from the portfolio below.</p>
        </label>
        <label class="mt-4 block">
          <span class="mb-1.5 block text-xs font-semibold">Designation / Goal</span>
          <input v-model="designation" type="text" placeholder="e.g. Become a senior frontend engineer in 12 months" class="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]" />
        </label>
      </section>

      <!-- Card 3: Manage Skills Portfolio -->
      <section class="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-5 shadow-sm">
        <h2 class="text-sm font-bold">Manage Skills Portfolio</h2>

        <p class="mt-4 text-xs font-semibold">What I Teach (Offers)</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <span v-for="(skill, i) in offers" :key="`offer-${skill.id}-${i}`" class="flex items-center gap-1.5 rounded-lg bg-[var(--success-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--success-text)]">
            {{ skill.name }}
            <button type="button" class="opacity-60 transition hover:opacity-100" title="Remove" @click="removeSkill(skills.indexOf(skill))">&times;</button>
          </span>
          <span v-if="!offers.length" class="text-xs italic text-[var(--text-secondary)]">No offers yet — add a skill you can teach.</span>
        </div>

        <p class="mt-4 text-xs font-semibold">What I Want (Wants)</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <span v-for="(skill, i) in wants" :key="`want-${skill.id}-${i}`" class="flex items-center gap-1.5 rounded-lg bg-[var(--warning-bg)] px-2.5 py-1 text-xs font-semibold text-[var(--warning-text)]">
            {{ skill.name }}
            <button type="button" class="opacity-60 transition hover:opacity-100" title="Remove" @click="removeSkill(skills.indexOf(skill))">&times;</button>
          </span>
          <span v-if="!wants.length" class="text-xs italic text-[var(--text-secondary)]">No wants yet — add a skill you want to learn.</span>
        </div>

        <!-- add skill row -->
        <div class="mt-5 grid grid-cols-1 gap-2 sm:grid-cols-[1fr_auto_auto_auto]">
          <input v-model="newSkillName" type="text" placeholder="Skill name (e.g. Vue.js)"
            class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]"
            @keyup.enter="submitSkill()" />
          <select v-model="newSkillType" class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]">
            <option value="OFFERS">Offers</option>
            <option value="WANTS">Wants</option>
          </select>
          <select v-model="newSkillProficiency" class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)]">
            <option v-for="level in experienceLevels" :key="level" :value="level">{{ level }}</option>
          </select>
          <button type="button" :disabled="isAdding" class="rounded-lg bg-[var(--accent-primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60" @click="submitSkill()">
            {{ isAdding ? 'Adding…' : '+ Add' }}
          </button>
        </div>

        <p class="mt-5 text-xs font-semibold text-[var(--text-secondary)]">Suggestions</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <button v-for="s in suggestions" :key="s" type="button" :disabled="isAdding || skills.some((x) => x.name.toLowerCase() === s.toLowerCase() && x.skill_type === newSkillType)"
            class="rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] px-3 py-1.5 text-xs font-semibold text-[var(--text-primary)] transition hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] disabled:cursor-not-allowed disabled:opacity-40"
            @click="submitSkill(s)">
            + {{ s }}
          </button>
        </div>
      </section>
    </div>

    <!-- Sticky footer -->
    <div class="fixed inset-x-0 bottom-0 z-10 border-t border-[var(--border-color)] bg-[var(--bg-surface)]/95 px-5 py-3 backdrop-blur lg:pl-60">
      <div class="mx-auto flex max-w-3xl items-center justify-end gap-3">
        <button type="button" class="rounded-lg border border-[var(--border-color)] px-4 py-2.5 text-sm font-semibold text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]" @click="previewProfile">
          Preview Profile
        </button>
        <button type="button" :disabled="isLoading" class="flex min-w-40 items-center justify-center gap-2 rounded-lg bg-[var(--accent-primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-70" @click="saveAndContinue">
          <svg v-if="isLoading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25" />
            <path d="M22 12a10 10 0 0 0-10-10" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
          </svg>
          {{ isLoading ? 'Saving…' : 'Save & Continue' }}
        </button>
      </div>
    </div>
  </AppLayout>
</template>
