import { request } from './client'

export function getProgressDashboard() {
  return request('/progress/dashboard')
}
