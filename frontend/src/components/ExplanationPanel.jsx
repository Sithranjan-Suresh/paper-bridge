export default function ExplanationPanel({ explanation }) {
  if (!explanation) {
    return (
      <p className="text-sm text-gray-500">
        A grounded explanation for this letter isn't available yet.
      </p>
    )
  }

  return (
    <div>
      <p className="whitespace-pre-line text-gray-800">{explanation.generated_text}</p>
      {explanation.source_citations?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {explanation.source_citations.map((citationId) => (
            <span
              key={citationId}
              className="rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs text-gray-600"
              title="Source passage from the policy corpus"
            >
              {citationId}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
