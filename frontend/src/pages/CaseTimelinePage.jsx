import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import TimelineList from '../components/TimelineList.jsx'

export default function CaseTimelinePage() {
  const { caseId } = useParams()
  const [timeline, setTimeline] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    api
      .getTimeline(caseId)
      .then((data) => {
        if (!cancelled) setTimeline(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [caseId])

  if (error) {
    return <div className="p-8 text-red-600">Failed to load case: {error}</div>
  }

  if (!timeline) {
    return <div className="p-8 text-gray-500">Loading case timeline…</div>
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-1 text-2xl font-semibold text-gray-900">{timeline.display_name}</h1>
      <p className="mb-6 text-sm text-gray-500">
        {timeline.documents.length} document{timeline.documents.length === 1 ? '' : 's'}, sorted by urgency
      </p>
      <TimelineList documents={timeline.documents} />
    </div>
  )
}
