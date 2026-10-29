import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { fetchCurrentUser, loginUser, registerUser } from '@/api/authApi'
import { clearToken, getToken, setToken } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getToken())
  const user = ref(null)
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => Boolean(token.value))

  function applySession(newToken) {
    token.value = newToken
    setToken(newToken)
  }

  async function login(credentials) {
    loading.value = true
    error.value = ''
    try {
      const data = await loginUser(credentials)
      applySession(data.access_token)
      await loadProfile()
      return user.value
    } catch (err) {
      error.value = normalizeError(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    error.value = ''
    try {
      await registerUser(payload)
      // Register endpoint returns the user, not a token — sign in right after.
      await login({ email: payload.email, password: payload.password })
      return user.value
    } catch (err) {
      error.value = normalizeError(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadProfile() {
    user.value = await fetchCurrentUser()
    return user.value
  }

  function logout() {
    token.value = null
    user.value = null
    error.value = ''
    clearToken()
  }

  function normalizeError(err) {
    const detail = err.detail
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join('. ')
    if (typeof detail === 'string') return detail
    return err.message || 'Request failed'
  }

  return { token, user, loading, error, isAuthenticated, login, register, loadProfile, logout }
})
