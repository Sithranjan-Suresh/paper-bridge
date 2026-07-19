const FEATURE_LABELS = {
  days_until_deadline: 'Deadline proximity',
  doc_type_base_severity: 'Document severity',
  consequence_keyword_score: 'Consequence language',
  notice_stage: 'Notice stage',
}

export default function UrgencyBreakdown({ urgency }) {
  if (!urgency) return null

  const entries = Object.entries(urgency.feature_breakdown).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
  const maxAbs = Math.max(...entries.map(([, v]) => Math.abs(v)), 1)

  return (
    <div>
      <div className="mb-3 flex items-baseline gap-2">
        <span className="text-3xl font-bold text-gray-900">{Math.round(urgency.score)}</span>
        <span className="text-sm text-gray-500">/ 100</span>
      </div>
      <div className="flex flex-col gap-2">
        {entries.map(([feature, contribution]) => (
          <div key={feature}>
            <div className="flex justify-between text-xs text-gray-600">
              <span>{FEATURE_LABELS[feature] || feature}</span>
              <span>{contribution.toFixed(1)}</span>
            </div>
            <div className="h-2 w-full rounded-full bg-gray-100">
              <div
                className={`h-2 rounded-full ${contribution >= 0 ? 'bg-blue-500' : 'bg-gray-400'}`}
                style={{ width: `${(Math.abs(contribution) / maxAbs) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
