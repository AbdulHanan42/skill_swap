import { request } from './client'

export function listSkillCatalog() {
  return request('/skills')
}
