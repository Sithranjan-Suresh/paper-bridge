import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import ExtractionPanel from '../components/ExtractionPanel.jsx'
import ExplanationPanel from '../components/ExplanationPanel.jsx'

const DOC_TYPE_LABELS = {
  uscis_notice: 'USCIS Notice',
  medicaid_snap_notice: 'Medicaid/SNAP Notice',
  school_enrollment_notice: 'School Enrollment Notice',
  housing_authority_notice: 'Housing Authority Notice',
}

export default function DocumentDetailPage() {
  const { documentId } = useParams()
  const [document, setDocument] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    api
      .getDocument(documentId)
      .then((data) => {
        if (!cancelled) setDocument(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [documentId])

  if (error) {
    return <div className="p-8 text-red-600">Failed to load document: {error}</div>
  }

  if (!document) {
    return <div className="p-8 text-gray-500">Loading document…</div>
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <Link to={`/case/${document.case_id}`} className="text-sm text-blue-600 hover:underline">
        ← Back to timeline
      </Link>

      <div className="mt-2 flex items-center gap-2">
        <h1 className="text-2xl font-semibold text-gray-900">
          {DOC_TYPE_LABELS[document.doc_type] || document.doc_type}
        </h1>
        {document.urgency && (
          <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-semibold text-gray-700">
            Urgency: {Math.round(document.urgency.score)}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-500">{document.agency}</p>

      {document.document_flagged_for_review && (
        <div className="mt-4 rounded-lg border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-800">
          This document was hard to read clearly. Some fields below may be inaccurate — please double-check
          them.
        </div>
      )}

      <section className="mt-6">
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">Extracted Details</h2>
        <ExtractionPanel entities={document.entities} />
      </section>

      <section className="mt-6">
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">What This Means</h2>
        <ExplanationPanel explanation={document.explanation} />
      </section>
    </div>
  )
}
