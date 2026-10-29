import { ref } from 'vue'

import { extractApiError } from '@/api/client'
import { requestSwap } from '@/api/profileApi'

export function useSwapRequests() {
  const sentIds = ref(new Set())
  const pendingIds = ref(new Set())
  const toast = ref('')
  const error = ref('')

  let toastTimer = null
  function showToast(message) {
    toast.value = message
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => (toast.value = ''), 3500)
  }

  function markSent(userId, message) {
    sentIds.value = new Set([...sentIds.value, userId])
    showToast(message)
  }

  async function request(userId, name) {
    if (pendingIds.value.has(userId) || sentIds.value.has(userId)) return
    pendingIds.value = new Set([...pendingIds.value, userId])
    try {
      await requestSwap(userId)
      markSent(userId, `Swap request sent to ${name}!`)
    } catch (err) {
      const msg = extractApiError(err)
      if (msg.toLowerCase().includes('already')) {
        markSent(userId, `You are already connected with ${name}.`)
      } else {
        error.value = msg
      }
    } finally {
      const next = new Set(pendingIds.value)
      next.delete(userId)
      pendingIds.value = next
    }
  }

  return { sentIds, pendingIds, toast, error, request }
}
