import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { extractApiError } from '@/api/client'
import {
  acceptSwapRequest,
  declineSwapRequest,
  fetchIncomingRequests,
  fetchMatchSuggestions,
  fetchSentRequests,
  requestSwap,
} from '@/api/matchApi'

export const useMatchStore = defineStore('matches', () => {
  const suggestions = ref([])
  const incoming = ref([])
  const sent = ref([])

  const loadingInbox = ref(false)
  const loadingSuggestions = ref(false)
  const loadedOnce = ref(false)
  const error = ref('')

  const actingIds = ref(new Set()) // match ids mid accept/decline
  const acceptedIds = ref(new Set()) // accepted rows kept on screen while routing to chat
  const fadingIds = ref(new Set()) // declined matches still animating out
  const sendingIds = ref(new Set()) // target user ids with a request in flight
  const requestedIds = ref(new Set()) // target user ids already requested

  const incomingCount = computed(() => incoming.value.length)
  const sentCount = computed(() => sent.value.length)

  function toggle(setRef, id, on) {
    const next = new Set(setRef.value)
    if (on) next.add(id)
    else next.delete(id)
    setRef.value = next
  }

  function isSending(userId) {
    return sendingIds.value.has(userId) || requestedIds.value.has(userId)
  }

  async function loadInbox() {
    loadingInbox.value = true
    error.value = ''
    try {
      const [incomingRows, sentRows] = await Promise.all([
        fetchIncomingRequests(),
        fetchSentRequests(),
      ])
      incoming.value = incomingRows
      sent.value = sentRows
      requestedIds.value = new Set(sentRows.map((row) => row.peer_id))
      loadedOnce.value = true
    } catch (err) {
      error.value = extractApiError(err)
    } finally {
      loadingInbox.value = false
    }
  }

  async function refresh() {
    // Silent re-poll so a peer's accept/decline lands without a manual reload.
    if (!loadedOnce.value || loadingInbox.value || document.hidden) return
    try {
      const [incomingRows, sentRows] = await Promise.all([
        fetchIncomingRequests(),
        fetchSentRequests(),
      ])
      const accepted = incoming.value.filter((row) => acceptedIds.value.has(row.match_id))
      incoming.value = [
        ...incomingRows.filter((row) => !acceptedIds.value.has(row.match_id)),
        ...accepted,
      ]
      sent.value = sentRows
      requestedIds.value = new Set(sentRows.map((row) => row.peer_id))
    } catch {
      /* keep the last known inbox until the next successful poll */
    }
  }

  async function loadSuggestions() {
    loadingSuggestions.value = true
    try {
      suggestions.value = await fetchMatchSuggestions()
    } catch (err) {
      error.value = extractApiError(err)
    } finally {
      loadingSuggestions.value = false
    }
  }

  async function send(targetUserId) {
    if (isSending(targetUserId)) return { ok: false, duplicate: true }
    toggle(sendingIds, targetUserId, true)
    try {
      await requestSwap(targetUserId)
      toggle(requestedIds, targetUserId, true)
      await loadInbox()
      return { ok: true }
    } catch (err) {
      return { ok: false, message: extractApiError(err) }
    } finally {
      toggle(sendingIds, targetUserId, false)
    }
  }

  async function respond(matchId, action) {
    if (actingIds.value.has(matchId) || acceptedIds.value.has(matchId)) {
      return { ok: false, duplicate: true }
    }
    toggle(actingIds, matchId, true)
    const call = action === 'accept' ? acceptSwapRequest : declineSwapRequest
    try {
      const updated = await call(matchId)
      if (action === 'accept') {
        acceptedIds.value = new Set([...acceptedIds.value, matchId])
        incoming.value = incoming.value.map((row) =>
          row.match_id === matchId ? updated : row,
        )
        sent.value = sent.value.filter((row) => row.match_id !== matchId)
      } else {
        toggle(fadingIds, matchId, true)
        setTimeout(() => {
          incoming.value = incoming.value.filter((row) => row.match_id !== matchId)
          sent.value = sent.value.filter((row) => row.match_id !== matchId)
          toggle(fadingIds, matchId, false)
        }, 320)
      }
      toggle(requestedIds, updated.peer_id, false)
      return { ok: true, request: updated }
    } catch (err) {
      return { ok: false, message: extractApiError(err) }
    } finally {
      toggle(actingIds, matchId, false)
    }
  }

  function reset() {
    suggestions.value = []
    incoming.value = []
    sent.value = []
    actingIds.value = new Set()
    acceptedIds.value = new Set()
    fadingIds.value = new Set()
    sendingIds.value = new Set()
    requestedIds.value = new Set()
    loadedOnce.value = false
    error.value = ''
  }

  return {
    suggestions,
    incoming,
    sent,
    loadingInbox,
    loadingSuggestions,
    error,
    actingIds,
    acceptedIds,
    fadingIds,
    sendingIds,
    requestedIds,
    incomingCount,
    sentCount,
    isSending,
    loadInbox,
    refresh,
    loadSuggestions,
    send,
    respond,
    reset,
  }
})
