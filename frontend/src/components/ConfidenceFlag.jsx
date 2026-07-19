import { useState } from 'react'

export default function ConfidenceFlag() {
  const [acknowledged, setAcknowledged] = useState(false)

  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
        Please verify
      </span>
      {!acknowledged && (
        <button
          type="button"
          onClick={() => setAcknowledged(true)}
          className="text-xs text-gray-400 underline hover:text-gray-600"
        >
          got it
        </button>
      )}
    </span>
  )
}
