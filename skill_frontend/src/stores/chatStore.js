import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { extractApiError } from '@/api/client'
import { fetchChatContacts, markChatRead } from '@/api/chatApi'

const byRecent = (a, b) => new Date(b.last_message_at) - new Date(a.last_message_at)

export const useChatStore = defineStore('chat', () => {
  const contacts = ref([])
  const loading = ref(false)
  const loadedOnce = ref(false)
  const error = ref('')

  const totalUnread = computed(() =>
    contacts.value.reduce((sum, contact) => sum + contact.unread_count, 0),
  )

  async function load() {
    loading.value = true
    error.value = ''
    try {
      contacts.value = (await fetchChatContacts()).sort(byRecent)
    } catch (err) {
      error.value = extractApiError(err)
    } finally {
      loading.value = false
      loadedOnce.value = true
    }
  }

  async function refresh() {
    // Silent re-poll so an unread badge appears without a reload or a skeleton.
    if (!loadedOnce.value || loading.value || document.hidden) return
    try {
      contacts.value = (await fetchChatContacts()).sort(byRecent)
    } catch {
      /* keep the last known conversations until the next poll succeeds */
    }
  }

  function markRead(matchId) {
    const contact = contacts.value.find((item) => item.id === matchId)
    if (!contact) return
    if (contact.unread_count) {
      contact.unread_count = 0
      markChatRead(matchId).catch(() => refresh())
    }
  }

  /** Keep the sidebar preview in step with a room that is currently open. */
  function receive(matchId, message) {
    const contact = contacts.value.find((item) => item.id === matchId)
    if (!contact) return
    contact.last_message = message.content || message.attachment?.filename || 'Attachment'
    contact.last_message_at = message.sent_at
    contact.last_message_mine = message.sender_id !== contact.peer_id
    contacts.value = [...contacts.value].sort(byRecent)
  }

  function reset() {
    contacts.value = []
    loadedOnce.value = false
    error.value = ''
  }

  return {
    contacts,
    loading,
    loadedOnce,
    error,
    totalUnread,
    load,
    refresh,
    markRead,
    receive,
    reset,
  }
})
