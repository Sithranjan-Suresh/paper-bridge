import TimelineEntry from './TimelineEntry.jsx'

export default function TimelineList({ documents, supersededDocumentIds = new Set() }) {
  if (!documents || documents.length === 0) {
    return <p className="text-gray-500">No documents uploaded yet.</p>
  }

  return (
    <div className="flex flex-col gap-3">
      {documents.map((document) => (
        <TimelineEntry
          key={document.id}
          document={document}
          isSuperseded={supersededDocumentIds.has(document.id)}
        />
      ))}
    </div>
  )
}
