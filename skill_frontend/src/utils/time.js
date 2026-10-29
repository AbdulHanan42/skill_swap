const DAY = 86_400_000

function startOfDay(value) {
  const date = value instanceof Date ? new Date(value) : new Date(value)
  date.setHours(0, 0, 0, 0)
  return date
}

/** "Today" / "Yesterday" / "Oct 24" */
export function formatDay(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  const days = Math.round((startOfDay(Date.now()) - startOfDay(date)) / DAY)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

/** 1.5 -> "1.5 hrs", 2 -> "2 hrs" */
export function formatHours(value) {
  const rounded = Math.round((Number(value) || 0) * 10) / 10
  return `${rounded % 1 === 0 ? rounded.toFixed(0) : rounded.toFixed(1)} hrs`
}
