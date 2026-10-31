import { request } from './client'

export function fetchMatchSuggestions() {
  return request('/matches/suggestions')
}

export function requestSwap(targetUserId) {
  return request(`/matches/request/${targetUserId}`, { method: 'POST' })
}

export function fetchIncomingRequests() {
  return request('/matches/requests/pending')
}

export function fetchSentRequests() {
  return request('/matches/requests/sent')
}

export function acceptSwapRequest(matchId) {
  return request(`/matches/requests/${matchId}/accept`, { method: 'PUT' })
}

export function declineSwapRequest(matchId) {
  return request(`/matches/requests/${matchId}/decline`, { method: 'PUT' })
}

export function fetchMatchDetail(matchId) {
  return request(`/matches/${matchId}`)
}
