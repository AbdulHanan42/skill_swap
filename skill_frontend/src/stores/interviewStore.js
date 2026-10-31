import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import {
  answerInterview,
  fetchInterviewStatus,
  resetInterview,
  skipInterview,
  startInterview,
  submitInterviewTask,
} from '@/api/interviewApi'
import { DEMO_TASK, demoStatus } from '@/utils/interviewFallback'

/**
 * Holds the interview screen exactly as the server describes it. When the API
 * cannot be reached at all the same shape is filled from the offline demo paper,
 * clearly flagged so nobody mistakes a local click-through for a real result.
 */
export const useInterviewStore = defineStore('interview', () => {
  const status = ref(null)
  const loading = ref(false)
  const submitting = ref(false)
  const error = ref('')
  const loadedOnce = ref(false)
  const demo = ref(false)

  const state = computed(() => status.value?.state ?? 'not_started')
  const step = computed(() => status.value?.step ?? 0)
  const skills = computed(() => status.value?.skills ?? [])
  const question = computed(() => status.value?.question ?? null)
  const task = computed(() => (demo.value ? { ...DEMO_TASK, submission: submission.value } : status.value?.task ?? null))
  const result = computed(() => status.value?.result ?? null)
  const totalQuestions = computed(() => status.value?.total_questions ?? 0)
  const answered = computed(() => status.value?.answered ?? 0)
  const submission = ref(null)
  const mcqComplete = computed(() => state.value === 'task' || state.value === 'verified')
  const finished = computed(() => state.value === 'verified')
  const skillLabel = computed(() => (skills.value.length ? skills.value.join(' & ') : 'General engineering'))
  const sidebarTag = computed(() => {
    if (demo.value || state.value === 'not_started') return ''
    return finished.value ? 'DONE' : 'ACTIVE'
  })

  function apply(payload) {
    status.value = payload
    loadedOnce.value = true
    return payload
  }

  async function load() {
    loading.value = true
    error.value = ''
    try {
      let payload = await fetchInterviewStatus()
      if (payload.state === 'not_started') {
        payload = await startInterview()
      }
      apply(payload)
    } catch (err) {
      error.value = err?.message || 'Could not reach the interview service.'
      demo.value = true
      apply(demoStatus())
    } finally {
      loading.value = false
    }
  }

  /** Silent poll that keeps the navigation badge honest; never surfaces errors. */
  async function refresh() {
    if (loading.value || demo.value || document.hidden) return
    try {
      apply(await fetchInterviewStatus())
    } catch {
      // A later poll or a manual retry picks it up.
    }
  }

  async function restart() {
    loading.value = true
    error.value = ''
    submission.value = null
    try {
      demo.value = false
      await resetInterview().catch(() => null)
      apply(await startInterview())
    } catch (err) {
      error.value = err?.message || 'Could not restart the interview.'
      demo.value = true
      apply(demoStatus())
    } finally {
      loading.value = false
    }
  }

  function walkDemo(record) {
    const screen = status.value
    const index = screen.questions.findIndex((item) => item.id === screen.question.id)
    screen.answers[screen.question.id] = record
    screen.answered = Object.keys(screen.answers).length
    const next = screen.questions[index + 1]
    if (next) {
      screen.question = { ...next, answered: screen.answered }
    } else {
      screen.question = null
      screen.state = 'task'
      screen.step = 1
    }
  }

  async function answer(option) {
    if (!question.value) return
    error.value = ''
    if (demo.value) {
      walkDemo({ selected: option, correct: option === question.value.answerIndex })
      return
    }
    try {
      apply(await answerInterview(question.value.id, option))
    } catch (err) {
      error.value = err?.message || 'Could not save that answer.'
    }
  }

  async function skip() {
    if (!question.value) return
    error.value = ''
    if (demo.value) {
      walkDemo({ selected: null, correct: false })
      return
    }
    try {
      apply(await skipInterview(question.value.id))
    } catch (err) {
      error.value = err?.message || 'Could not skip that question.'
    }
  }

  async function submitTask(file) {
    submitting.value = true
    error.value = ''
    try {
      if (demo.value) {
        submission.value = { filename: file.name, size: file.size, mime_type: file.type }
        error.value = 'The backend is offline, so this submission cannot be graded. Reconnect and submit again.'
        return null
      }
      apply(await submitInterviewTask(file))
      return status.value
    } catch (err) {
      error.value = err?.message || 'Could not upload your solution.'
      return null
    } finally {
      submitting.value = false
    }
  }

  function reset() {
    status.value = null
    loadedOnce.value = false
    demo.value = false
    submission.value = null
    error.value = ''
  }

  return {
    status,
    loading,
    submitting,
    error,
    loadedOnce,
    demo,
    state,
    step,
    skills,
    skillLabel,
    question,
    task,
    result,
    totalQuestions,
    answered,
    submission,
    mcqComplete,
    finished,
    sidebarTag,
    load,
    refresh,
    restart,
    answer,
    skip,
    submitTask,
    reset,
  }
})
