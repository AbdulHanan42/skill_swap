import { computed, ref } from 'vue'

import { useMatchStore } from '@/stores/matchStore'

/**
 * Sending side of Skill Matching. Each suggestion already carries its
 * `request_state` from the server, so the button only needs this for the
 * in-flight flag and the result message.
 */
export function useSwapRequests() {
  const store = useMatchStore()
  const toast = ref('')
  const error = ref('')

  const pendingIds = computed(() => store.sendingIds)

  async function request(userId, name) {
    const result = await store.send(userId)
    if (result.ok) {
      toast.value = `Swap request sent to ${name}!`
      return 'requested_by_me'
    }
    if (result.duplicate) return null
    if ((result.message || '').toLowerCase().includes('already connected')) {
      toast.value = `You are already connected with ${name}.`
      return 'connected'
    }
    error.value = result.message || 'Could not send the request.'
    return null
  }

  return { pendingIds, toast, error, request }
}
