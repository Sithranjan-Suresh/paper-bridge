export default function ConflictBanner({ event }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-orange-200 bg-orange-50 p-4">
      <span className="mt-0.5 text-lg" aria-hidden="true">
        ⚠️
      </span>
      <div>
        <p className="font-medium text-orange-900">This letter updates a previous one</p>
        <p className="text-sm text-orange-800">{event.description}</p>
      </div>
    </div>
  )
}
