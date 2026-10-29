import { request } from './client'

export function listSkillCatalog() {
  return request('/skills')
}

export function fetchProfile() {
  return request('/profile/me')
}

export function updateProfile({ fullName, bio, designation }) {
  const body = {}
  if (fullName !== undefined) body.full_name = fullName
  if (bio !== undefined) body.bio = bio
  if (designation !== undefined) body.designation = designation
  return request('/profile/me', { method: 'PUT', body })
}

export function addSkill({ skillName, category, skillType, proficiency }) {
  return request('/profile/skills', {
    method: 'POST',
    body: {
      skill_name: skillName,
      category: category || null,
      skill_type: skillType,
      proficiency,
    },
  })
}

export function getDashboardOverview() {
  return request('/dashboard/overview')
}
