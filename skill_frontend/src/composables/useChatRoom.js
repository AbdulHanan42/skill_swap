import { onUnmounted, ref, watch } from 'vue'

import { extractApiError, getToken, websocketUrl } from '@/api/client'
import { fetchChatHistory } from '@/api/matchApi'

/**
 * Live chat pipe for one match: REST history first, then WebSocket for new turns.
 * `getMatchId` is re-evaluated on change so the view can switch rooms in place.
 */
export function useChatRoom(getMatchId) {
  const messages = ref([])
  const loading = ref(true)
  const error = ref('')
  const connected = ref(false)
  const disconnected = ref(false)

  let socket = null
  let currentId = null

  function closeSocket() {
    if (!socket) return
    const dying = socket
    socket = null
    dying.onclose = null
    dying.close()
    connected.value = false
  }

  async function loadHistory(matchId) {
    loading.value = true
    error.value = ''
    try {
      const history = await fetchChatHistory(matchId, { pageSize: 100 })
      messages.value = history.items
    } catch (err) {
      error.value = extractApiError(err)
      messages.value = []
    } finally {
      loading.value = false
    }
  }

  function connect() {
    const matchId = getMatchId()
    if (!matchId) return
    closeSocket()
    const token = getToken()
    if (!token) {
      error.value = 'Your session expired. Sign in again to chat.'
      return
    }
    disconnected.value = false
    socket = new WebSocket(websocketUrl(`/chat/${matchId}?token=${encodeURIComponent(token)}`))
    socket.onopen = () => {
      connected.value = true
    }
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      if (payload.error) {
        error.value = payload.error
        return
      }
      error.value = ''
      if (!messages.value.some((item) => item.id === payload.id)) {
        messages.value = [...messages.value, payload]
      }
    }
    socket.onclose = () => {
      connected.value = false
      socket = null
      disconnected.value = true
    }
  }

  function send(content) {
    const text = content.trim()
    if (!text || !socket || socket.readyState !== WebSocket.OPEN) return false
    socket.send(JSON.stringify({ content: text }))
    return true
  }

  watch(
    getMatchId,
    async (matchId) => {
      if (!matchId || matchId === currentId) return
      currentId = matchId
      await loadHistory(matchId)
      connect()
    },
    { immediate: true },
  )

  onUnmounted(closeSocket)

  return { messages, loading, error, connected, disconnected, send, connect }
}
