import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import TimelineList from '../components/TimelineList.jsx'
import ConflictBanner from '../components/ConflictBanner.jsx'
import UploadDropzone from '../components/UploadDropzone.jsx'
import SkeletonBlock from '../components/SkeletonBlock.jsx'

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
    return (
      <div className="mx-auto max-w-3xl p-8">
        <SkeletonBlock className="mb-2 h-8 w-72" />
        <SkeletonBlock className="mb-6 h-4 w-48" />
        <div className="flex flex-col gap-3">
          <SkeletonBlock className="h-20 w-full" />
          <SkeletonBlock className="h-20 w-full" />
          <SkeletonBlock className="h-20 w-full" />
        </div>
      </div>
    )
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
        <p className="mt-2 text-center text-xs text-gray-400">
          No document handy?{' '}
          <a href="/sample-letter.pdf" download className="text-blue-600 underline hover:text-blue-700">
            Download a sample USCIS letter
          </a>{' '}
          to try the pipeline live.
        </p>
      </div>
    </div>
  )
}
