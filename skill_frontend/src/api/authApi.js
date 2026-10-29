import { request } from './client'

export function registerUser({ fullName, email, password, designation, bio }) {
  return request('/auth/register', {
    method: 'POST',
    body: {
      email,
      password,
      full_name: fullName,
      designation: designation || null,
      bio: bio || null,
    },
  })
}

export function loginUser({ email, password }) {
  // Backend uses OAuth2PasswordRequestForm, so credentials go as form data
  return request('/auth/login', {
    method: 'POST',
    form: { username: email, password },
  })
}

export function fetchCurrentUser() {
  return request('/profile/me')
}
