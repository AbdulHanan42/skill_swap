<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { extractApiError } from '@/api/client'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const submitting = ref(false)
const formError = ref('')
const showPassword = ref(false)
const fieldErrors = reactive({})

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  designation: '',
  bio: '',
})

const isRegister = computed(() => mode.value === 'register')

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

/* ---------- brand panel visuals ---------- */

const avatars = [
  { x: 200, y: 210, size: 22, ring: 'ring-teal-400/70 glow-teal', bg: '#134e4a', skin: '#f3c3a0', hair: '#312e81', shirt: '#5eead4' },
  { x: 92, y: 118, size: 14, ring: 'ring-pink-400/70 glow-pink', bg: '#4a044e', skin: '#e8b088', hair: '#1e1b4b', shirt: '#f9a8d4' },
  { x: 308, y: 112, size: 14, ring: 'ring-orange-400/70 glow-orange', bg: '#431407', skin: '#c98a5b', hair: '#0f172a', shirt: '#fdba74' },
  { x: 64, y: 282, size: 13, ring: 'ring-violet-400/70 glow-violet', bg: '#2e1065', skin: '#f3c3a0', hair: '#7c3aed', shirt: '#c4b5fd' },
  { x: 334, y: 272, size: 13, ring: 'ring-emerald-400/70 glow-emerald', bg: '#022c22', skin: '#8d5a3b', hair: '#111827', shirt: '#6ee7b7' },
  { x: 202, y: 52, size: 12, ring: 'ring-sky-400/70 glow-sky', bg: '#082f49', skin: '#e8b088', hair: '#3b0764', shirt: '#7dd3fc' },
]

const links = [
  'M200,210 Q130,175 92,118',
  'M200,210 Q275,170 308,112',
  'M200,210 Q120,255 64,282',
  'M200,210 Q285,250 334,272',
  'M200,210 Q245,125 202,52',
]

const badges = [
  { text: '💻 Python', cls: 'left-[2%] top-[18%]', delay: '0s' },
  { text: '🎨 UX UI', cls: 'left-[8%] bottom-[6%]', delay: '1.4s' },
  { text: '📈 Marketing', cls: 'right-[2%] top-[34%]', delay: '0.7s' },
  { text: '🤝 Matched!', cls: 'right-[6%] bottom-[20%]', delay: '2.1s' },
  { text: '⚡ Matched!', cls: 'left-[30%] top-[2%]', delay: '1s' },
]

const particles = Array.from({ length: 22 }, (_, i) => ({
  left: `${(i * 47 + 13) % 100}%`,
  top: `${(i * 31 + 7) % 100}%`,
  size: 2 + (i % 3) * 2,
  delay: `${(i % 7) * 1.1}s`,
  duration: `${6 + (i % 5) * 2.5}s`,
}))

/* ---------- auth logic ---------- */

function switchMode(next) {
  mode.value = next
  formError.value = ''
  clearFieldErrors()
}

function clearFieldErrors() {
  Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key])
}

function validate() {
  clearFieldErrors()
  if (!EMAIL_PATTERN.test(form.email.trim())) {
    fieldErrors.email = 'Enter a valid email address'
  }
  if (form.password.length < (isRegister.value ? 8 : 1)) {
    fieldErrors.password = isRegister.value
      ? 'Password must be at least 8 characters'
      : 'Password is required'
  }
  if (isRegister.value && !form.fullName.trim()) {
    fieldErrors.fullName = 'Full name is required'
  }
  return Object.keys(fieldErrors).length === 0
}

function mapServerErrors(err) {
  const status = err.status
  formError.value = ''
  clearFieldErrors()
  if (status === 409) {
    fieldErrors.email = 'Email already registered — try logging in'
  } else if (status === 401) {
    formError.value = 'Incorrect email or password'
  } else {
    formError.value = extractApiError(err)
  }
}

async function handleSubmit() {
  if (!validate()) return
  submitting.value = true
  formError.value = ''
  try {
    if (isRegister.value) {
      await auth.register({
        fullName: form.fullName.trim(),
        email: form.email.trim(),
        password: form.password,
        designation: form.designation.trim(),
        bio: form.bio.trim(),
      })
    } else {
      await auth.login({ email: form.email.trim(), password: form.password })
    }
    router.push({ name: 'dashboard' })
  } catch (err) {
    mapServerErrors(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen overflow-hidden bg-[#0a0d1a] text-slate-100 lg:grid lg:grid-cols-2">
    <!-- ============ Left: brand splasher ============ -->
    <aside class="relative hidden flex-col justify-between overflow-hidden p-12 lg:flex">
      <!-- animated mesh background -->
      <div class="mesh-bg absolute inset-0" />
      <div class="mesh-bg mesh-alt absolute inset-0" />

      <!-- particle nodes -->
      <span
        v-for="(p, i) in particles"
        :key="`p-${i}`"
        class="particle absolute rounded-full bg-indigo-300/50"
        :style="{ left: p.left, top: p.top, width: `${p.size}px`, height: `${p.size}px`, animationDelay: p.delay, animationDuration: p.duration }"
      ></span>

      <!-- logo -->
      <div class="relative z-10 flex items-center gap-3">
        <div class="logo-glow flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-xl font-bold text-white">⇄</div>
        <span class="text-2xl font-semibold tracking-tight">Skill Swap</span>
      </div>

      <!-- headline -->
      <div class="relative z-10">
        <h2 class="heading-glow text-4xl font-bold leading-tight text-white xl:text-[2.75rem]">
          Teach one skill.<br />Learn another.
        </h2>
        <p class="mt-4 max-w-md text-indigo-200">
          Get matched with people who want to learn exactly what you teach — and teach
          exactly what you want to learn.
        </p>

        <!-- animated matching network -->
        <div class="relative mx-auto mt-4 aspect-square w-full max-w-[350px]">
          <svg viewBox="0 0 400 400" class="absolute inset-0 h-full w-full" fill="none">
            <path
              v-for="(d, i) in links"
              :key="`l-${i}`"
              :d="d"
              stroke="rgba(165,180,252,0.55)"
              stroke-width="1.6"
              stroke-dasharray="5 7"
              stroke-linecap="round"
              class="animate-dash"
              :style="{ animationDelay: `${i * 0.5}s` }"
            />
          </svg>

          <div
            v-for="(a, i) in avatars"
            :key="`a-${i}`"
            class="drift absolute -translate-x-1/2 -translate-y-1/2 overflow-hidden rounded-full bg-slate-900 ring-2"
            :class="[a.ring, i === 0 ? 'z-[2]' : 'z-[1]']"
            :style="{ left: `${a.x / 4}%`, top: `${a.y / 4}%`, width: `${a.size}%`, aspectRatio: '1', animationDelay: `${i * 0.8}s`, animationDuration: `${5 + i}s` }"
          >
            <svg viewBox="0 0 120 120" class="h-full w-full">
              <rect width="120" height="120" :fill="a.bg" />
              <path d="M22,120 C26,90 42,80 60,80 C78,80 94,90 98,120 Z" :fill="a.shirt" />
              <path d="M60,88 L60,120" :stroke="a.bg" stroke-width="3" />
              <circle cx="60" cy="46" r="21" :fill="a.hair" />
              <circle cx="60" cy="50" r="19" :fill="a.skin" />
              <circle cx="53" cy="50" r="2.2" fill="#1e1b4b" />
              <circle cx="67" cy="50" r="2.2" fill="#1e1b4b" />
              <path d="M53,58 Q60,64 67,58" stroke="#1e1b4b" stroke-width="2.5" fill="none" stroke-linecap="round" />
            </svg>
          </div>

          <span
            v-for="(b, i) in badges"
            :key="`b-${i}`"
            class="badge-glow drift absolute rounded-xl px-3 py-1.5 text-xs font-semibold text-white"
            :class="b.cls"
            :style="{ animationDelay: b.delay, animationDuration: `${6 + (i % 3)}s` }"
          >{{ b.text }}</span>
        </div>
      </div>

      <p class="relative z-10 text-sm text-indigo-300/70">AI-guided interviews · Smart matching · Real-time chat</p>
    </aside>

    <!-- ============ Right: auth glass card ============ -->
    <main class="relative flex min-h-screen items-center justify-center px-4 py-12 sm:px-8">
      <!-- deep-background accents -->
      <div class="pointer-events-none absolute inset-0 overflow-hidden">
        <div class="absolute -right-24 top-16 w-56 rotate-6 rounded-2xl border border-white/10 bg-indigo-500/10 p-4 opacity-40 backdrop-blur-sm">
          <p class="mb-2 text-[10px] uppercase tracking-widest text-indigo-300">Active swaps</p>
          <svg viewBox="0 0 200 60" class="w-full">
            <polyline points="0,50 30,38 60,44 90,20 120,28 150,10 200,18" stroke="#818cf8" stroke-width="2.5" fill="none" stroke-linecap="round" />
          </svg>
        </div>
        <div class="absolute -left-20 bottom-20 w-48 -rotate-3 rounded-2xl border border-white/10 bg-violet-500/10 p-4 opacity-30 backdrop-blur-sm">
          <p class="mb-2 text-[10px] uppercase tracking-widest text-violet-300">Skills learned</p>
          <div class="flex items-end gap-1.5">
            <span class="h-6 w-3 rounded-t bg-violet-400/60" />
            <span class="h-10 w-3 rounded-t bg-violet-400/80" />
            <span class="h-4 w-3 rounded-t bg-violet-400/50" />
            <span class="h-12 w-3 rounded-t bg-violet-400" />
            <span class="h-7 w-3 rounded-t bg-violet-400/70" />
          </div>
        </div>
        <div class="absolute right-[12%] top-[10%] h-1.5 w-1.5 animate-pulse rounded-full bg-fuchsia-400/70" />
        <div class="absolute left-[8%] top-[24%] h-1 w-1 animate-pulse rounded-full bg-indigo-300/70" style="animation-delay:.8s" />
        <div class="absolute bottom-[14%] right-[22%] h-1 w-1 animate-pulse rounded-full bg-teal-300/70" style="animation-delay:1.6s" />
      </div>

      <div class="relative w-full max-w-md">
        <!-- mobile brand -->
        <div class="mb-8 flex items-center gap-3 lg:hidden">
          <div class="logo-glow flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-lg font-bold">⇄</div>
          <span class="text-xl font-semibold">Skill Swap</span>
        </div>

        <!-- glass card -->
        <div class="rounded-2xl border border-white/10 bg-[#101326]/60 p-6 shadow-[0_0_70px_rgba(99,102,241,0.18)] backdrop-blur-xl sm:p-8">
          <!-- sliding tab toggle -->
          <div class="relative mb-8 grid grid-cols-2 rounded-xl border border-white/10 bg-[#0c0f20]/70 p-1">
            <span
              class="absolute inset-y-1 left-1 w-[calc(50%-4px)] rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 shadow-[0_0_20px_rgba(124,58,237,0.55)] transition-transform duration-300 ease-out"
              :style="{ transform: isRegister ? 'translateX(100%)' : 'translateX(0)' }"
            ></span>
            <button
              type="button"
              class="relative z-10 rounded-lg py-2 text-sm font-medium transition-colors"
              :class="!isRegister ? 'text-white' : 'text-slate-400 hover:text-slate-200'"
              @click="switchMode('login')"
            >
              Log in
            </button>
            <button
              type="button"
              class="relative z-10 rounded-lg py-2 text-sm font-medium transition-colors"
              :class="isRegister ? 'text-white' : 'text-slate-400 hover:text-slate-200'"
              @click="switchMode('register')"
            >
              Create account
            </button>
          </div>

          <h1 class="text-2xl font-bold text-white">
            {{ isRegister ? 'Create your profile' : 'Welcome back' }}
          </h1>
          <p class="mt-1 mb-6 text-sm text-slate-400">
            {{ isRegister
              ? 'Register and start finding skill-swap partners.'
              : 'Log in to continue your skill swaps.' }}
          </p>

          <p v-if="formError" class="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {{ formError }}
          </p>

          <form class="space-y-4" novalidate @submit.prevent="handleSubmit">
            <Transition name="slide-fade">
              <div v-if="isRegister">
                <label for="fullName" class="mb-1.5 block text-sm font-medium text-slate-300">Full name</label>
                <div class="relative">
                  <span class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  </span>
                  <input
                    id="fullName"
                    v-model="form.fullName"
                    type="text"
                    autocomplete="name"
                    placeholder="Ayesha Khan"
                    class="w-full rounded-lg border bg-[#0c0f20]/70 py-2.5 pl-10 pr-4 text-sm outline-none transition-all duration-300 placeholder:text-slate-600 focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
                    :class="fieldErrors.fullName ? 'border-red-500/60' : 'border-white/10'"
                  />
                </div>
                <p v-if="fieldErrors.fullName" class="mt-1 text-xs text-red-400">{{ fieldErrors.fullName }}</p>
              </div>
            </Transition>

            <div>
              <label for="email" class="mb-1.5 block text-sm font-medium text-slate-300">Email</label>
              <div class="relative">
                <span class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>
                </span>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  autocomplete="email"
                  placeholder="you@example.com"
                  class="w-full rounded-lg border bg-[#0c0f20]/70 py-2.5 pl-10 pr-4 text-sm outline-none transition-all duration-300 placeholder:text-slate-600 focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
                  :class="fieldErrors.email ? 'border-red-500/60' : 'border-white/10'"
                />
              </div>
              <p v-if="fieldErrors.email" class="mt-1 text-xs text-red-400">{{ fieldErrors.email }}</p>
            </div>

            <div>
              <label for="password" class="mb-1.5 block text-sm font-medium text-slate-300">Password</label>
              <div class="relative">
                <span class="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  :autocomplete="isRegister ? 'new-password' : 'current-password'"
                  :placeholder="isRegister ? 'Minimum 8 characters' : 'Your password'"
                  class="w-full rounded-lg border bg-[#0c0f20]/70 py-2.5 pl-10 pr-11 text-sm outline-none transition-all duration-300 placeholder:text-slate-600 focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
                  :class="fieldErrors.password ? 'border-red-500/60' : 'border-white/10'"
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-violet-400"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="!showPassword" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c6.5 0 10 8 10 8a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.5 13.5 0 0 0 2 12s3.5 8 10 8a9.12 9.12 0 0 0 5.39-1.61"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><path d="m2 2 20 20"/></svg>
                </button>
              </div>
              <p v-if="fieldErrors.password" class="mt-1 text-xs text-red-400">{{ fieldErrors.password }}</p>
            </div>

            <Transition name="slide-fade">
              <div v-if="isRegister">
                <label for="designation" class="mb-1.5 block text-sm font-medium text-slate-300">
                  Designation <span class="text-slate-500">(optional)</span>
                </label>
                <input
                  id="designation"
                  v-model="form.designation"
                  type="text"
                  placeholder="Frontend Developer"
                  class="w-full rounded-lg border border-white/10 bg-[#0c0f20]/70 px-4 py-2.5 text-sm outline-none transition-all duration-300 placeholder:text-slate-600 focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
                />
              </div>
            </Transition>

            <Transition name="slide-fade">
              <div v-if="isRegister">
                <label for="bio" class="mb-1.5 block text-sm font-medium text-slate-300">
                  Bio <span class="text-slate-500">(optional)</span>
                </label>
                <textarea
                  id="bio"
                  v-model="form.bio"
                  rows="3"
                  placeholder="What do you teach, and what do you want to learn?"
                  class="w-full resize-none rounded-lg border border-white/10 bg-[#0c0f20]/70 px-4 py-2.5 text-sm outline-none transition-all duration-300 placeholder:text-slate-600 focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
                ></textarea>
              </div>
            </Transition>

            <button
              type="submit"
              :disabled="submitting"
              class="btn-glow mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 py-2.5 text-sm font-semibold text-white transition-all duration-300 hover:scale-[1.02] hover:from-violet-500 hover:to-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <span
                v-if="submitting"
                class="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
              ></span>
              <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              {{ submitting ? (isRegister ? 'Creating account…' : 'Logging in…') : (isRegister ? 'Create account' : 'Log in') }}
            </button>
          </form>

          <p class="mt-6 text-center text-sm text-slate-400">
            {{ isRegister ? 'Already have an account?' : "Don't have an account?" }}
            <button
              type="button"
              class="font-medium text-violet-400 transition hover:text-violet-300 hover:[text-shadow:0_0_14px_rgba(167,139,250,0.6)]"
              @click="switchMode(isRegister ? 'login' : 'register')"
            >
              {{ isRegister ? 'Log in' : 'Register' }}
            </button>
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* animated mesh waves */
.mesh-bg {
  background:
    radial-gradient(60% 80% at 15% 20%, rgba(99, 102, 241, 0.55), transparent 60%),
    radial-gradient(50% 70% at 85% 15%, rgba(124, 58, 237, 0.5), transparent 60%),
    radial-gradient(70% 90% at 50% 90%, rgba(15, 62, 181, 0.65), transparent 65%),
    linear-gradient(135deg, #05021a 0%, #120a3a 55%, #0f3eb5 130%);
  animation: mesh-pulse 12s ease-in-out infinite alternate;
}
.mesh-alt {
  opacity: 0.5;
  animation: mesh-pulse-alt 16s ease-in-out infinite alternate;
}
@keyframes mesh-pulse {
  from { transform: scale(1); opacity: 1; }
  to { transform: scale(1.12) translate(-2%, -2%); opacity: 0.85; }
}
@keyframes mesh-pulse-alt {
  from { transform: scale(1.1) translate(2%, 1%); opacity: 0.35; }
  to { transform: scale(1); opacity: 0.6; }
}

/* floating particle nodes */
.particle {
  animation: particle-float linear infinite;
  filter: blur(0.4px);
}
@keyframes particle-float {
  0% { transform: translateY(0); opacity: 0.15; }
  50% { transform: translateY(-26px); opacity: 0.7; }
  100% { transform: translateY(-52px); opacity: 0; }
}

/* glowing dashed connection paths */
.animate-dash {
  animation: dash 2.4s linear infinite;
}
@keyframes dash {
  to { stroke-dashoffset: -24; }
}

/* drift for avatars & badges */
.drift {
  animation-name: drift;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}
@keyframes drift {
  0%, 100% { margin-top: 0; }
  50% { margin-top: -10px; }
}

/* glowing rings per avatar color */
.glow-teal { box-shadow: 0 0 22px rgba(45, 212, 191, 0.45); }
.glow-pink { box-shadow: 0 0 18px rgba(244, 114, 182, 0.4); }
.glow-orange { box-shadow: 0 0 18px rgba(251, 146, 60, 0.4); }
.glow-violet { box-shadow: 0 0 18px rgba(167, 139, 250, 0.4); }
.glow-emerald { box-shadow: 0 0 18px rgba(52, 211, 153, 0.4); }
.glow-sky { box-shadow: 0 0 18px rgba(56, 189, 248, 0.4); }

/* floating skill badges */
.badge-glow {
  background: rgba(16, 19, 38, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  box-shadow: 0 0 24px rgba(99, 102, 241, 0.35);
}

/* logo & headline glow */
.logo-glow { box-shadow: 0 0 26px rgba(99, 102, 241, 0.65); }
.heading-glow { text-shadow: 0 0 32px rgba(129, 140, 248, 0.45); }
.btn-glow { box-shadow: 0 8px 30px rgba(109, 40, 217, 0.45); }
.btn-glow:hover { box-shadow: 0 10px 40px rgba(124, 58, 237, 0.65); }

/* register-field transitions */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s ease-in; }
.slide-fade-enter-from,
.slide-fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
