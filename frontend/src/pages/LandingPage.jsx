import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

export default function LandingPage() {
  const navigate = useNavigate()
  const [loadingDemo, setLoadingDemo] = useState(false)
  const [error, setError] = useState(null)

  const handleViewDemo = async () => {
    setLoadingDemo(true)
    setError(null)
    try {
      const demoCase = await api.getDemoCase()
      navigate(`/case/${demoCase.id}`)
    } catch (err) {
      setError(err.message)
      setLoadingDemo(false)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold">PaperBridge</h1>
      <button
        type="button"
        onClick={handleViewDemo}
        disabled={loadingDemo}
        className="mt-4 rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {loadingDemo ? 'Loading…' : 'View Demo Case'}
      </button>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  )
}
