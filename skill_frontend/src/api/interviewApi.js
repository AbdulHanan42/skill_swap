import { request, requestBlob } from './client'

export function fetchInterviewStatus() {
  return request('/interview/status')
}

export function startInterview() {
  return request('/interview/start', { method: 'POST' })
}

export function answerInterview(questionId, selectedOption) {
  return request('/interview/answer', {
    method: 'POST',
    body: { question_id: questionId, selected_option: selectedOption },
  })
}

export function skipInterview(questionId) {
  return request('/interview/skip', { method: 'POST', body: { question_id: questionId } })
}

export function submitInterviewTask(file) {
  const form = new FormData()
  form.append('file', file)
  return request('/interview/submit-task', { method: 'POST', formData: form })
}

export function resetInterview() {
  return request('/interview/reset', { method: 'POST' })
}

export function fetchTaskBrief() {
  return requestBlob('/interview/task-brief')
}
