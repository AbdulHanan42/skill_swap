export function formatBytes(bytes) {
  const size = Number(bytes) || 0
  if (size < 1024) return `${size} B`
  const units = ['KB', 'MB', 'GB']
  const exponent = Math.min(Math.floor(Math.log(size) / Math.log(1024)) - 1, units.length - 1)
  const value = size / 1024 ** (exponent + 1)
  return `${value >= 10 ? Math.round(value) : value.toFixed(1)} ${units[exponent]}`
}

export function isImage(attachment) {
  const mime = attachment?.mime_type ?? ''
  // The backend refuses to serve SVG inline, so never try to render one here.
  return mime.startsWith('image/') && mime !== 'image/svg+xml'
}

export function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename || 'download'
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
