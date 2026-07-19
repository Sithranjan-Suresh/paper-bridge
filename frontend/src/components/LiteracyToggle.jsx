const LEVELS = [
  { value: 'simple', label: 'Simple' },
  { value: 'standard', label: 'Standard' },
  { value: 'detailed', label: 'Detailed' },
]

export default function LiteracyToggle({ value, onChange, disabled }) {
  return (
    <div className="inline-flex rounded-md border border-gray-200 bg-gray-50 p-0.5">
      {LEVELS.map((level) => (
        <button
          key={level.value}
          type="button"
          disabled={disabled}
          onClick={() => onChange(level.value)}
          className={`rounded px-3 py-1 text-sm font-medium transition disabled:opacity-50 ${
            value === level.value ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {level.label}
        </button>
      ))}
    </div>
  )
}
