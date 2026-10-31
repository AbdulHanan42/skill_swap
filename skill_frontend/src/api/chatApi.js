import { request, requestBlob } from './client'

export const MAX_UPLOAD_BYTES = 5 * 1024 * 1024

export function fetchChatContacts() {
  return request('/chat/contacts')
}

export function fetchChatHistory(matchId, { page = 1, pageSize = 50 } = {}) {
  return request(`/chat/${matchId}/history?page=${page}&page_size=${pageSize}`)
}

export function markChatRead(matchId) {
  return request(`/chat/${matchId}/read`, { method: 'POST' })
}

export function uploadChatAttachment(matchId, file, caption = '') {
  const form = new FormData()
  form.append('file', file)
  form.append('caption', caption)
  return request(`/chat/${matchId}/attachments`, { method: 'POST', formData: form })
}

export function fetchChatAttachment(messageId) {
  return requestBlob(`/chat/attachments/${messageId}`)
}

