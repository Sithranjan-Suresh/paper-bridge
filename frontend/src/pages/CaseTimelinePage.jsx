import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import TimelineList from '../components/TimelineList.jsx'
import ConflictBanner from '../components/ConflictBanner.jsx'
import UploadDropzone from '../components/UploadDropzone.jsx'

export default function CaseTimelinePage() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const [timeline, setTimeline] = useState(null)
  const [error, setError] = useState(null)

  const loadTimeline = useCallback(() => {
    return api.getTimeline(caseId).then(setTimeline)
  }, [caseId])

  useEffect(() => {
    let cancelled = false
    loadTimeline().catch((err) => {
      if (!cancelled) setError(err.message)
    })
    return () => {
      cancelled = true
    }
  }, [loadTimeline])

  const handleUpload = async (file) => {
    const document = await api.uploadDocument(caseId, file)
    navigate(`/document/${document.id}`)
  }

  if (error) {
    return <div className="p-8 text-red-600">Failed to load case: {error}</div>
  }

  if (!timeline) {
    return <div className="p-8 text-gray-500">Loading case timeline…</div>
  }

  const conflictEvents = timeline.events.filter((e) => e.event_type === 'supersedes' || e.event_type === 'conflicts_with')
  const supersededDocumentIds = new Set(
    conflictEvents.map((e) => e.related_document_id).filter((id) => id != null),
  )

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-1 text-2xl font-semibold text-gray-900">{timeline.display_name}</h1>
      <p className="mb-6 text-sm text-gray-500">
        {timeline.documents.length} document{timeline.documents.length === 1 ? '' : 's'}, sorted by urgency
      </p>

      {conflictEvents.length > 0 && (
        <div className="mb-6 flex flex-col gap-3">
          {conflictEvents.map((event, i) => (
            <ConflictBanner key={i} event={event} />
          ))}
        </div>
      )}

      <TimelineList documents={timeline.documents} supersededDocumentIds={supersededDocumentIds} />

      <div className="mt-8">
        <UploadDropzone onUpload={handleUpload} />
      </div>
    </div>
  )
}
