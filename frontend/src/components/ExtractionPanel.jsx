import ConfidenceFlag from './ConfidenceFlag.jsx'

const ENTITY_LABELS = {
  deadline: 'Deadline',
  case_number: 'Case Number',
  agency: 'Agency',
  required_action: 'Required Action',
}

export default function ExtractionPanel({ entities }) {
  if (!entities || entities.length === 0) {
    return <p className="text-sm text-gray-500">No structured fields were extracted from this letter.</p>
  }

  return (
    <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {entities.map((entity) => (
        <div key={entity.entity_type} className="rounded-lg border border-gray-200 p-3">
          <dt className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-gray-500">
            {ENTITY_LABELS[entity.entity_type] || entity.entity_type}
            {entity.flagged_for_review && <ConfidenceFlag />}
          </dt>
          <dd className="mt-1 text-sm font-medium text-gray-900">{entity.value || '—'}</dd>
        </div>
      ))}
    </dl>
  )
}
