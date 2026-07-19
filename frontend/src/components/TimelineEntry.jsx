import { Link } from 'react-router-dom'

const DOC_TYPE_LABELS = {
  uscis_notice: 'USCIS Notice',
  medicaid_snap_notice: 'Medicaid/SNAP Notice',
  school_enrollment_notice: 'School Enrollment Notice',
  housing_authority_notice: 'Housing Authority Notice',
}

function urgencyColor(score) {
  if (score == null) return 'bg-gray-200 text-gray-700'
  if (score >= 70) return 'bg-red-100 text-red-700'
  if (score >= 40) return 'bg-amber-100 text-amber-700'
  return 'bg-emerald-100 text-emerald-700'
}

export default function TimelineEntry({ document }) {
  return (
    <Link
      to={`/document/${document.id}`}
      className="flex items-center justify-between gap-4 rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition hover:shadow-md"
    >
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">
            {DOC_TYPE_LABELS[document.doc_type] || document.doc_type}
          </span>
          {document.flagged_for_review && (
            <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
              Please verify
            </span>
          )}
        </div>
        <p className="truncate text-sm text-gray-500">{document.agency || 'Unknown agency'}</p>
        {document.deadline && (
          <p className="text-sm text-gray-500">Deadline: {document.deadline}</p>
        )}
      </div>
      <div className={`shrink-0 rounded-full px-3 py-1 text-sm font-semibold ${urgencyColor(document.urgency_score)}`}>
        {document.urgency_score != null ? Math.round(document.urgency_score) : '—'}
      </div>
    </Link>
  )
}
