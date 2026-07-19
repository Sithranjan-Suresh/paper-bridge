import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

const AGENCIES = ['USCIS', 'Medicaid / SNAP', 'School District', 'Housing Authority']

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
    <div className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <span className="text-lg font-semibold tracking-tight">PaperBridge</span>
        <button
          type="button"
          onClick={handleViewDemo}
          disabled={loadingDemo}
          className="rounded-md border border-gray-300 px-4 py-1.5 text-sm font-medium text-gray-700 transition hover:border-gray-400 disabled:opacity-60"
        >
          {loadingDemo ? 'Loading…' : 'View Demo Case'}
        </button>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-3xl px-6 pt-16 pb-20 text-center">
        <p className="mb-4 text-sm font-medium uppercase tracking-widest text-blue-600">
          Case memory for families navigating the system
        </p>
        <h1 className="text-4xl font-semibold leading-tight tracking-tight text-gray-900 sm:text-5xl">
          One confusing letter isn't the problem.
          <br />
          Four letters from four agencies is.
        </h1>
        <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-gray-600">
          Immigrant and refugee families managing USCIS, Medicaid, school enrollment, and housing
          correspondence don't lose track of one letter — they lose track of how letters connect. PaperBridge
          reads every letter, remembers every prior one, and flags the moment something changes.
        </p>
        <div className="mt-10 flex items-center justify-center gap-3">
          <button
            type="button"
            onClick={handleViewDemo}
            disabled={loadingDemo}
            className="rounded-md bg-blue-600 px-6 py-3 font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-60"
          >
            {loadingDemo ? 'Loading…' : 'View Demo Case →'}
          </button>
        </div>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

        <div className="mt-12 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-gray-400">
          {AGENCIES.map((agency) => (
            <span key={agency}>{agency}</span>
          ))}
        </div>
      </section>

      {/* Problem / differentiator */}
      <section className="border-t border-gray-100 bg-gray-50">
        <div className="mx-auto grid max-w-5xl gap-8 px-6 py-16 sm:grid-cols-2">
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-400">
              Document explainer tools
            </p>
            <p className="text-gray-700">
              Treat every upload as an isolated event. Explain letter #4 without knowing what letter #1 said —
              so a superseded deadline, a changed case number, or a conflicting instruction slips through
              silently.
            </p>
          </div>
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-6">
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-600">PaperBridge</p>
            <p className="text-gray-800">
              Reads each letter, then checks it against everything already on file for that case. When a new
              letter changes something you already knew, it tells you explicitly — before you act on outdated
              information.
            </p>
          </div>
        </div>
      </section>

      {/* Feature strip */}
      <section className="mx-auto max-w-5xl px-6 py-16">
        <div className="grid gap-8 sm:grid-cols-3">
          <Feature
            title="Explainable, not a black box"
            body="A real classical-ML urgency model shows exactly why a letter is scored the way it is — deadline proximity, severity, consequence language, notice stage."
          />
          <Feature
            title="Grounded, cited explanations"
            body="Plain-language explanations are generated only from a curated policy corpus, with source citations — reducing hallucination risk in a high-stakes domain."
          />
          <Feature
            title="Confidence you can trust"
            body="Low-confidence extractions are flagged for review instead of silently presented as fact. Nothing important disappears unacknowledged."
          />
        </div>
      </section>

      <footer className="border-t border-gray-100 px-6 py-8 text-center text-sm text-gray-400">
        PaperBridge — built for families managing correspondence across agencies that don't talk to each other.
      </footer>
    </div>
  )
}

function Feature({ title, body }) {
  return (
    <div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="mt-1 text-sm leading-relaxed text-gray-600">{body}</p>
    </div>
  )
}
