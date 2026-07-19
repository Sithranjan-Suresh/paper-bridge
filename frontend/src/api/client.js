const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options)
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}))
    throw new Error(detail.detail || `Request failed: ${response.status}`)
  }
  return response.json()
}

export const api = {
  getTimeline: (caseId) => request(`/cases/${caseId}/timeline`),
  getDocument: (documentId) => request(`/documents/${documentId}`),
  getExplanation: (documentId, literacyLevel) =>
    request(`/documents/${documentId}/explanation?literacy_level=${literacyLevel}`),
  uploadDocument: (caseId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request(`/cases/${caseId}/documents`, { method: 'POST', body: formData })
  },
  createCase: (displayName) =>
    request('/cases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ display_name: displayName }),
    }),
}
