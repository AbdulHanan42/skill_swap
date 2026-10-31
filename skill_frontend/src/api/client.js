const TOKEN_KEY = 'skillswap_access_token'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  constructor(status, detail) {
    super(formatDetail(detail) || `Request failed with status ${status}`)
    this.status = status
    this.detail = detail
  }
}

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    // FastAPI 422 validation errors
    return detail.map((item) => item.msg).join('. ')
  }
  if (typeof detail === 'string') {
    return detail
  }
  return null
}

async function send(path, options) {
  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, options)
  } catch {
    throw new ApiError(0, 'Network error. Is the backend running?')
  }
  if (!response.ok) {
    const data = response.status === 204 ? null : await response.json().catch(() => null)
    // A 401 while a token is attached means the session expired — a 401 with no
    // token is just a failed login attempt and must stay on the form.
    if (response.status === 401 && getToken()) {
      clearToken()
      if (window.location.pathname !== '/auth') {
        window.location.assign('/auth')
      }
    }
    throw new ApiError(response.status, data?.detail)
  }
  return response
}

function authHeaders(withoutContentType) {
  const headers = {}
  if (getToken()) {
    headers.Authorization = `Bearer ${getToken()}`
  }
  if (!withoutContentType) headers['Content-Type'] = 'application/json'
  return headers
}

export async function request(path, { method = 'GET', body, form, formData } = {}) {
  const options = { method, headers: authHeaders(Boolean(formData)) }
  if (formData) {
    // The browser sets the multipart boundary itself, so no Content-Type here.
    options.body = formData
  } else if (form) {
    options.body = new URLSearchParams(form).toString()
    options.headers['Content-Type'] = 'application/x-www-form-urlencoded'
  } else if (body !== undefined) {
    options.body = JSON.stringify(body)
  }
  const response = await send(path, options)
  return response.status === 204 ? null : response.json()
}

export async function requestBlob(path) {
  const response = await send(path, { method: 'GET', headers: authHeaders(true) })
  return response.blob()
}


export function extractApiError(error) {
  if (error instanceof ApiError) {
    return error.message
  }
  return error?.message || 'Network error. Is the backend running?'
}

export function websocketUrl(path) {
  const { protocol, host } = new URL(BASE_URL)
  return `${protocol === 'https:' ? 'wss:' : 'ws:'}//${host}/ws${path}`
}
