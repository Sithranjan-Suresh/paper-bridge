import { useLayoutEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'
import { api } from '../api/client.js'
import { withColdStartNotice } from '../api/withColdStartNotice.js'
import '../landing.css'

gsap.registerPlugin(ScrollTrigger)

const LETTERS = [
  {
    id: 'uscis1',
    agency: 'USCIS',
    color: '#3b82f6',
    title: 'Notice of Action · I-797C',
    caseno: 'MSC2190012345',
    start: { x: 0.13, y: 0.38, r: -7, s: 1 },
    slot: { y: 0.2, side: -1 },
    superseded: true,
  },
  {
    id: 'uscis2',
    agency: 'USCIS',
    color: '#3b82f6',
    title: 'Biometrics Rescheduled',
    caseno: 'MSC2190012345',
    start: { x: 0.86, y: 0.39, r: 5, s: 0.96 },
    slot: { y: 0.44, side: 1 },
  },
  {
    id: 'medicaid',
    agency: 'Medicaid / SNAP',
    color: '#10b981',
    title: 'Redetermination Notice',
    caseno: 'SNP-88213',
    start: { x: 0.68, y: 0.72, r: -4, s: 0.9 },
    slot: { y: 0.58, side: -1 },
  },
  {
    id: 'school',
    agency: 'School District',
    color: '#8b5cf6',
    title: 'Enrollment Confirmation',
    caseno: 'RS-4471',
    start: { x: 0.16, y: 0.74, r: 6, s: 0.88 },
    slot: { y: 0.71, side: 1 },
  },
  {
    id: 'housing',
    agency: 'Housing Authority',
    color: '#f59e0b',
    title: 'Recertification Received',
    caseno: 'HV-30291',
    start: { x: 0.46, y: 0.6, r: -3, s: 0.85 },
    slot: { y: 0.84, side: -1 },
  },
]

function Wordmark({ className = '' }) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <svg width="26" height="26" viewBox="0 0 26 26" fill="none" aria-hidden="true">
        <rect x="2" y="13" width="9" height="11" rx="2" fill="#3b82f6" opacity="0.9" />
        <rect x="15" y="13" width="9" height="11" rx="2" fill="#10b981" opacity="0.9" />
        <path d="M4 13C4 6.5 22 6.5 22 13" stroke="#0f172a" strokeWidth="2.2" strokeLinecap="round" />
      </svg>
      <span className="pb-serif text-lg font-semibold tracking-tight">PaperBridge</span>
    </span>
  )
}

function LetterCard({ letter }) {
  return (
    <div className="pb-letter" data-letter={letter.id}>
      <div className="drift">
        {letter.superseded && <span className="badge-superseded">Superseded</span>}
        <div className="agency">
          <span className="dot" style={{ background: letter.color }} />
          {letter.agency}
        </div>
        <div className="title">{letter.title}</div>
        <div className="caseno">Case {letter.caseno}</div>
        <div className="lines">
          <i /><i /><i />
        </div>
      </div>
    </div>
  )
}

export default function LandingPage() {
  const navigate = useNavigate()
  const rootRef = useRef(null)
  const lenisRef = useRef(null)
  const [loadingDemo, setLoadingDemo] = useState(false)
  const [demoError, setDemoError] = useState(null)
  const [wakingBackend, setWakingBackend] = useState(false)

  const handleSkipIntro = () => {
    const target = document.getElementById('after-film')
    if (!target) return
    // Lenis intercepts scroll (including programmatic smooth-scrollTo) to
    // drive it through its own animation loop, so hand control back to the
    // browser first, then jump straight to the first content section — not
    // just past the pin boundary, which leaves a blank seam/fade gap in view.
    if (lenisRef.current) {
      lenisRef.current.destroy()
      lenisRef.current = null
    }
    const headerOffset = 72
    window.scrollTo(0, target.getBoundingClientRect().top + window.scrollY - headerOffset)
    // An instant jump lands the visitor directly on this section without
    // ever crossing its reveal-on-scroll trigger, so it would otherwise sit
    // at opacity:0 forever. Force it visible; later sections still reveal
    // normally as the visitor continues scrolling into them.
    gsap.set(target.querySelectorAll('.pb-reveal'), { opacity: 1, y: 0 })
  }

  const handleViewDemo = async () => {
    setLoadingDemo(true)
    setDemoError(null)
    setWakingBackend(false)
    try {
      const demoCase = await withColdStartNotice(api.getDemoCase(), () => setWakingBackend(true))
      navigate(`/case/${demoCase.id}`)
    } catch (err) {
      setDemoError(err.message)
      setLoadingDemo(false)
      setWakingBackend(false)
    }
  }

  useLayoutEffect(() => {
    const root = rootRef.current
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const params = new URLSearchParams(window.location.search)
    const jump = params.get('jump')
    if (jump !== null) window.history.scrollRestoration = 'manual'

    const cleanupFns = []
    let lenis = null
    if (!reduced && jump === null) {
      lenis = new Lenis({ lerp: 0.09, smoothWheel: true })
      lenisRef.current = lenis
      lenis.on('scroll', ScrollTrigger.update)
      gsap.ticker.add((t) => lenis.raf(t * 1000))
      gsap.ticker.lagSmoothing(0)
    }

    const ctx = gsap.context(() => {
      const stage = root.querySelector('.pb-stage')
      const q = (sel) => root.querySelector(sel)
      const letterEls = Object.fromEntries(
        LETTERS.map((l) => [l.id, root.querySelector(`[data-letter="${l.id}"]`)]),
      )

      const W = () => stage.clientWidth
      const H = () => stage.clientHeight
      const mobile = () => W() < 640

      const spineOffset = () => (mobile() ? 0.26 : 0.16) * W()
      const spineScale = () => (mobile() ? 0.58 : 0.7)
      const meetX = (side) => (mobile() ? (side < 0 ? 0.28 : 0.72) : side < 0 ? 0.33 : 0.67)

      // ----- initial scatter -----
      LETTERS.forEach((l) => {
        gsap.set(letterEls[l.id], {
          xPercent: -50,
          yPercent: -50,
          x: () => l.start.x * W(),
          y: () => l.start.y * H(),
          rotation: l.start.r,
          scale: () => (mobile() ? l.start.s * 0.82 : l.start.s),
        })
      })
      gsap.set('.pb-milestone', {
        xPercent: -50,
        yPercent: -50,
        x: () => 0.5 * W(),
        y: () => 0.3 * H(),
        scale: 0,
        opacity: 0,
      })
      gsap.set('.pb-connected', {
        xPercent: -50,
        yPercent: -50,
        x: () => 0.5 * W(),
        y: () => 0.93 * H(),
        scale: 0,
        opacity: 0,
      })

      // svg dash setup
      // pixel-space SVG geometry; pathLength="1" normalizes dash draw-on
      const arc = q('.pb-arc')
      const spine = q('.pb-spine')
      const ticks = gsap.utils.toArray(root.querySelectorAll('.pb-tick'))
      const layoutNet = () => {
        const w = W()
        const h = H()
        const ax1 = meetX(-1) * w
        const ax2 = meetX(1) * w
        const ay = 0.42 * h
        const peak = 0.31 * h
        arc.setAttribute('d', `M${ax1},${ay} C${ax1 + (ax2 - ax1) * 0.24},${peak} ${ax2 - (ax2 - ax1) * 0.24},${peak} ${ax2},${ay}`)
        spine.setAttribute('x1', 0.5 * w)
        spine.setAttribute('x2', 0.5 * w)
        spine.setAttribute('y1', 0.14 * h)
        spine.setAttribute('y2', 0.9 * h)
        LETTERS.forEach((l) => {
          const t = root.querySelector(`[data-tick="${l.id}"]`)
          t.setAttribute('x1', 0.5 * w)
          t.setAttribute('x2', 0.5 * w + l.slot.side * 0.06 * w)
          t.setAttribute('y1', l.slot.y * h)
          t.setAttribute('y2', l.slot.y * h)
        })
      }
      layoutNet()
      ScrollTrigger.addEventListener('refreshInit', layoutNet)
      cleanupFns.push(() => ScrollTrigger.removeEventListener('refreshInit', layoutNet))
      gsap.set([arc, spine, ...ticks], { strokeDasharray: 1, strokeDashoffset: 1, opacity: 0 })

      gsap.set(['.pb-beat-2', '.pb-beat-3', '.pb-beat-4', '.pb-beat-5'], { opacity: 0, y: 26 })
      gsap.set('.badge-superseded', { opacity: 0, y: 4 })
      gsap.set('.pb-fade-out', { opacity: 0 })

      const finalState = () => {
        LETTERS.forEach((l) => {
          gsap.set(letterEls[l.id], {
            x: 0.5 * W() + l.slot.side * spineOffset(),
            y: l.slot.y * H(),
            rotation: l.slot.side * 1.2,
            scale: spineScale(),
            opacity: l.superseded ? 0.55 : 1,
          })
        })
        gsap.set('.pb-milestone', { x: 0.5 * W(), y: 0.32 * H(), scale: spineScale() + 0.1, opacity: 1 })
        gsap.set('.pb-connected', { scale: 1, opacity: 1 })
        gsap.set([spine, ...ticks], { strokeDashoffset: 0, opacity: 1 })
        gsap.set('.badge-superseded', { opacity: 1, y: 0 })
        gsap.set('.pb-beat-5', { opacity: 1, y: 0 })
        gsap.set(['.pb-beat-1', '.pb-hint'], { opacity: 0 })
      }

      if (reduced) {
        finalState()
        window.__ready = true
        return
      }

      // ----- on-load hero reveal (not scrubbed) -----
      // Skipped entirely when jumping straight to a scroll position — this
      // reveal targets .pb-hint/.pb-char independently of the scrub timeline,
      // and its fixed delay can otherwise stomp their scroll-driven state.
      const startingAtTop = jump === null || +jump === 0
      if (startingAtTop) {
        const chars = gsap.utils.toArray(root.querySelectorAll('.pb-char'))
        gsap.from(chars, {
          yPercent: 120,
          stagger: 0.035,
          duration: 0.9,
          ease: 'power4.out',
          delay: 0.15,
          overwrite: 'auto',
        })
        gsap.from('.pb-tagline, .pb-hint', {
          opacity: 0,
          y: 14,
          duration: 0.8,
          delay: 0.7,
          ease: 'power2.out',
          overwrite: 'auto',
          onStart: function () {
            // guard against the delayed entrance firing after the visitor has
            // already scrolled past chapter 1 (scrub timeline owns opacity then)
            if (window.scrollY > 40) this.progress(1)
          },
        })
      } else {
        gsap.set('.pb-char', { yPercent: 0 })
      }

      // ambient drift on inner wrappers (never scrubbed)
      gsap.utils.toArray(root.querySelectorAll('.pb-letter .drift')).forEach((el, i) => {
        gsap.to(el, {
          y: gsap.utils.random(-9, 9),
          rotation: gsap.utils.random(-1.4, 1.4),
          duration: gsap.utils.random(2.6, 3.8),
          delay: i * 0.2,
          ease: 'sine.inOut',
          yoyo: true,
          repeat: -1,
        })
      })

      // ----- the film (single pinned scrubbed master) -----
      const tl = gsap.timeline({
        defaults: { ease: 'power2.inOut' },
        scrollTrigger: {
          trigger: '.pb-film',
          start: 'top top',
          end: '+=430%',
          pin: true,
          scrub: jump !== null ? true : 1,
          invalidateOnRefresh: true,
        },
      })

      // ch1 → hero copy releases
      tl.to('.pb-beat-1', { opacity: 0, y: -50, duration: 0.7 }, 0.15)
      tl.to('.pb-hint', { opacity: 0, duration: 0.3 }, 0.15)

      // ch2 — the two USCIS letters find each other
      tl.to(letterEls.uscis1, { x: () => meetX(-1) * W(), y: () => 0.42 * H(), rotation: -2, scale: 1, duration: 1.2 }, 1.0)
      tl.to(letterEls.uscis2, { x: () => meetX(1) * W(), y: () => 0.42 * H(), rotation: 2, scale: 1, duration: 1.2 }, 1.0)
      tl.to([letterEls.medicaid, letterEls.school, letterEls.housing], { opacity: 0.4, scale: '-=0.1', duration: 1.0 }, 1.05)
      tl.to(arc, { opacity: 1, duration: 0.15 }, 2.05)
      tl.to(arc, { strokeDashoffset: 0, duration: 0.8, ease: 'power1.inOut' }, 2.1)
      tl.to('.pb-beat-2', { opacity: 1, y: 0, duration: 0.5 }, 2.5)
      tl.to('.pb-beat-2', { opacity: 0, y: -22, duration: 0.45 }, 3.6)

      // ch3 — the conflict
      tl.to('.pb-milestone', { scale: 1, opacity: 1, duration: 0.55, ease: 'back.out(2)' }, 3.7)
      tl.to('.pb-milestone', {
        keyframes: [
          { scale: 1.13, duration: 0.22 },
          { scale: 1, duration: 0.22 },
          { scale: 1.13, duration: 0.22 },
          { scale: 1, duration: 0.22 },
        ],
      }, 4.3)
      tl.to('.pb-beat-3', { opacity: 1, y: 0, duration: 0.5 }, 4.1)
      tl.to(letterEls.uscis1, { opacity: 0.55, duration: 0.5 }, 4.6)
      tl.to('.badge-superseded', { opacity: 1, y: 0, duration: 0.4 }, 4.7)
      tl.to('.pb-beat-3', { opacity: 0, y: -22, duration: 0.45 }, 5.4)
      tl.to(arc, { opacity: 0, duration: 0.4 }, 5.4)

      // ch4 — assembly
      tl.to([letterEls.medicaid, letterEls.school, letterEls.housing], { opacity: 1, duration: 0.5 }, 5.6)
      tl.to(spine, { opacity: 1, duration: 0.15 }, 5.7)
      tl.to(spine, { strokeDashoffset: 0, duration: 1.5, ease: 'power1.inOut' }, 5.75)
      LETTERS.forEach((l, i) => {
        tl.to(letterEls[l.id], {
          x: () => 0.5 * W() + l.slot.side * spineOffset(),
          y: () => l.slot.y * H(),
          rotation: l.slot.side * 1.2,
          scale: () => spineScale(),
          duration: 1.0,
          ease: 'power3.inOut',
        }, 5.9 + i * 0.22)
      })
      tl.to('.pb-milestone', {
        x: () => 0.5 * W(),
        y: () => 0.32 * H(),
        scale: () => spineScale() + 0.1,
        duration: 1.0,
        ease: 'power3.inOut',
      }, 6.1)
      ticks.forEach((t, i) => {
        tl.to(t, { opacity: 1, strokeDashoffset: 0, duration: 0.3 }, 6.7 + i * 0.16)
      })
      tl.to('.pb-beat-4', { opacity: 1, y: 0, duration: 0.5 }, 6.6)
      tl.to('.pb-beat-4', { opacity: 0, y: -22, duration: 0.45 }, 7.9)

      // ch5 — connected; the finished timeline glides right to make room for the close
      tl.to('.pb-world', { x: () => (mobile() ? 0 : 0.17 * W()), duration: 1.2, ease: 'power2.inOut' }, 7.9)
      tl.to('.pb-connected', { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(1.8)' }, 8.1)
      tl.to('.pb-beat-5', { opacity: 1, y: 0, duration: 0.6 }, 8.4)
      tl.to('.pb-fade-out', { opacity: 1, duration: 1.0, ease: 'none' }, 9.0)

      // ----- after-film reveals (created AFTER the pin — ordering law) -----
      gsap.utils.toArray(root.querySelectorAll('.pb-reveal')).forEach((el) => {
        gsap.to(el, {
          opacity: 1,
          y: 0,
          duration: 0.9,
          ease: 'power3.out',
          scrollTrigger: { trigger: el, start: 'top 85%', once: true },
        })
      })

      // dev contract — force-settle the scrubbed timeline's progress directly;
      // scrub:1 inertia otherwise leaves the tween lagging behind an instant jump
      const settle = () => {
        ScrollTrigger.refresh()
        if (jump !== null) {
          window.scrollTo(0, +jump || 0)
          ScrollTrigger.update()
          if (tl.scrollTrigger) tl.progress(tl.scrollTrigger.progress).pause()
        }
        window.__ready = true
      }
      if (document.fonts?.ready) document.fonts.ready.then(settle)
      else settle()
    }, root)

    return () => {
      cleanupFns.forEach((fn) => fn())
      ctx.revert()
      if (lenis && lenisRef.current === lenis) lenis.destroy()
      lenisRef.current = null
      delete window.__ready
    }
  }, [])

  const demoLabel = (idle) => {
    if (wakingBackend) return 'Waking up the server…'
    if (loadingDemo) return 'Opening…'
    return idle
  }

  const demoBtn = (extra = '') => (
    <div>
      <button
        type="button"
        onClick={handleViewDemo}
        disabled={loadingDemo}
        className={`rounded-full bg-[#0f172a] px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-[#1e293b] disabled:opacity-60 ${extra}`}
      >
        {demoLabel('See the Martinez family’s case →')}
      </button>
      {wakingBackend && (
        <p className="mt-2 text-xs text-[#94a3b8]">
          Free-tier hosting naps when idle — first load can take up to a minute.
        </p>
      )}
    </div>
  )

  return (
    <div ref={rootRef} className="pb-landing">
      {/* fixed chrome */}
      <header className="pb-header">
        <Wordmark />
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleSkipIntro}
            className="hidden text-sm font-medium text-[#475569] underline decoration-[#cfc7b4] underline-offset-4 transition hover:text-[#0f172a] sm:inline"
          >
            Skip intro
          </button>
          <button
            type="button"
            onClick={handleViewDemo}
            disabled={loadingDemo}
            className="rounded-full border border-[#e7e1d4] bg-white/70 px-4 py-1.5 text-sm font-medium text-[#0f172a] transition hover:border-[#cfc7b4] disabled:opacity-60"
          >
            {demoLabel('View Demo Case')}
          </button>
        </div>
      </header>

      {/* ---------- THE FILM ---------- */}
      <section className="pb-film">
        <div className="pb-stage">
          {/* connections */}
          <div className="pb-world absolute inset-0">
          <svg className="pb-net" aria-hidden="true">
            <path className="pb-arc" pathLength="1" stroke="#3b82f6" strokeWidth="2" />
            <line className="pb-spine" pathLength="1" stroke="#94a3b8" strokeWidth="1.5" />
            {LETTERS.map((l) => (
              <line key={l.id} className="pb-tick" data-tick={l.id} pathLength="1" stroke="#94a3b8" strokeWidth="1.5" />
            ))}
          </svg>

          {/* letters */}
          {LETTERS.map((l) => (
            <LetterCard key={l.id} letter={l} />
          ))}

          {/* milestone + terminal node */}
          <div className="pb-milestone">
            <span className="tick" />
            Deadline changed · Jul 9 → Jul 31
          </div>
          <div className="pb-connected">
            <svg width="15" height="15" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <circle cx="10" cy="10" r="9" fill="#10b981" />
              <path d="M6 10.5l2.6 2.6L14 7.5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Everything connected
          </div>
          </div>

          {/* beats */}
          <div className="pb-beat pb-beat-1 inset-x-0 top-[16%] text-center">
            <h1 className="pb-serif mx-auto max-w-4xl px-6 text-[clamp(2.6rem,7vw,5.2rem)] font-medium leading-[1.04] tracking-tight text-[#0f172a]">
              <span className="block overflow-hidden">
                {'PaperBridge'.split('').map((c, i) => (
                  <span key={i} className="pb-char inline-block">{c}</span>
                ))}
              </span>
            </h1>
            <p className="pb-tagline mx-auto mt-5 max-w-md px-6 text-base leading-relaxed text-[#475569] sm:text-lg">
              Government agencies don’t talk to each other.
              <span className="font-semibold text-[#0f172a]"> PaperBridge does.</span>
            </p>
          </div>

          <div className="pb-beat pb-beat-2 inset-x-0 top-[58%] text-center">
            <h2 className="mx-auto max-w-xl px-6 text-[clamp(1.5rem,3.4vw,2.4rem)]">
              They’re talking about the <em>same case.</em>
            </h2>
            <div className="mt-4">
              <span className="pb-chip">
                <span className="h-1.5 w-1.5 rounded-full bg-[#3b82f6]" />
                Case MSC2190012345 · matched
              </span>
            </div>
          </div>

          <div className="pb-beat pb-beat-3 inset-x-0 top-[60%] text-center">
            <h2 className="mx-auto max-w-xl px-6 text-[clamp(1.5rem,3.4vw,2.4rem)]">
              A deadline changed.
              <span className="block text-[#b45309]">PaperBridge caught it.</span>
            </h2>
          </div>

          <div className="pb-beat pb-beat-4 left-[6%] top-[38%] max-w-[280px] sm:left-[8%]">
            <h2 className="text-[clamp(1.4rem,2.8vw,2.1rem)]">
              Your letters, in order. Finally.
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-[#475569]">
              Every agency, one timeline — sorted by what actually needs you first.
            </p>
          </div>

          <div className="pb-beat pb-beat-5 left-[6%] top-[34%] max-w-[360px] sm:left-[8%]" style={{ pointerEvents: 'auto' }}>
            <h2 className="text-[clamp(1.7rem,3.2vw,2.6rem)]">Everything connected.</h2>
            <p className="mt-4 text-[15px] leading-relaxed text-[#475569]">
              PaperBridge isn’t a document analyzer. It’s the memory your family’s case never had.
            </p>
            <div className="mt-6">{demoBtn()}</div>
            {demoError && <p className="mt-2 text-sm text-red-600">{demoError}</p>}
          </div>

          <div className="pb-hint">
            <span>Scroll</span>
            <span className="wheel" />
          </div>

          {/* seam: film → content */}
          <div className="pb-fade-out pointer-events-none absolute inset-x-0 bottom-0 h-[38vh] bg-gradient-to-b from-transparent to-[#faf8f4]" />
        </div>
      </section>

      {/* ---------- AFTER THE FILM ---------- */}
      <section id="after-film" className="mx-auto max-w-5xl px-6 py-24 sm:py-32">
        <div className="pb-reveal">
          <p className="pb-section-label">Why PaperBridge</p>
          <h2 className="pb-serif mt-3 max-w-2xl text-[clamp(1.9rem,4vw,3rem)] font-medium leading-tight tracking-tight">
            Case memory, not document memory.
          </h2>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2">
          <div className="pb-reveal pb-glass p-7">
            <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-[#94a3b8]">
              Document explainer tools
            </p>
            <p className="leading-relaxed text-[#475569]">
              Treat every upload as an isolated event. They explain letter #4 without knowing what
              letter #1 said — so a superseded deadline or a conflicting instruction slips through
              silently.
            </p>
          </div>
          <div className="pb-reveal pb-glass border-[#bfdbfe] bg-[#eff6ff]/70 p-7">
            <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-[#2563eb]">
              PaperBridge
            </p>
            <p className="leading-relaxed text-[#1e293b]">
              Reads each letter, then checks it against everything already on file for that case.
              When a new letter changes something you already knew, it tells you explicitly — before
              you act on outdated information.
            </p>
          </div>
        </div>
      </section>

      <section className="bg-[#f3f0ea]">
        <div className="mx-auto max-w-5xl px-6 py-24">
          <div className="grid gap-6 sm:grid-cols-3">
            {[
              {
                t: 'Explainable, not a black box',
                b: 'A real classical-ML urgency model shows exactly why a letter scores the way it does — deadline proximity, severity, consequence language, notice stage.',
              },
              {
                t: 'Grounded, cited answers',
                b: 'Plain-language explanations are generated only from a curated policy corpus, with source citations — because in this domain, a wrong answer has real consequences.',
              },
              {
                t: 'Honest about uncertainty',
                b: 'Low-confidence extractions are flagged for review instead of presented as fact. Nothing important disappears unacknowledged.',
              },
            ].map((f) => (
              <div key={f.t} className="pb-reveal pb-glass p-7">
                <h3 className="pb-serif text-xl font-medium">{f.t}</h3>
                <p className="mt-3 text-sm leading-relaxed text-[#475569]">{f.b}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-24 sm:py-28">
        <div className="pb-reveal overflow-hidden rounded-3xl bg-[#0f172a] px-8 py-16 text-center text-white sm:px-16">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#60a5fa]">
            No signup · no setup
          </p>
          <h2 className="pb-serif mx-auto mt-4 max-w-xl text-[clamp(1.8rem,3.6vw,2.7rem)] font-medium leading-tight">
            Watch a real case make sense of itself.
          </h2>
          <p className="mx-auto mt-4 max-w-md text-[15px] leading-relaxed text-slate-300">
            Five letters, four agencies, one changed deadline — already loaded and connected.
          </p>
          <div className="mt-8 flex justify-center">
            <button
              type="button"
              onClick={handleViewDemo}
              disabled={loadingDemo}
              className="rounded-full bg-white px-7 py-3 text-sm font-semibold text-[#0f172a] shadow-lg transition hover:bg-[#eff6ff] disabled:opacity-60"
            >
              {demoLabel('View Demo Case →')}
            </button>
          </div>
          {wakingBackend && (
            <p className="mt-3 text-xs text-slate-400">
              Free-tier hosting naps when idle — first load can take up to a minute.
            </p>
          )}
          {demoError && <p className="mt-3 text-sm text-red-300">{demoError}</p>}
        </div>
      </section>

      <section className="border-t border-[#e7e1d4] bg-[#f3f0ea] px-6 py-16">
        <div className="pb-reveal mx-auto max-w-3xl text-center">
          <p className="pb-section-label">How it's built</p>
          <p className="mx-auto mt-3 max-w-xl text-[15px] leading-relaxed text-[#475569]">
            Classification, extraction, and urgency scoring are real classical ML — sentence-transformer
            embeddings, spaCy NER, a trained gradient-boosted model — running locally, not LLM calls.
          </p>
          <div className="mx-auto mt-6 inline-flex items-center gap-2 rounded-full border border-[#e7e1d4] bg-white px-4 py-2 text-sm text-[#475569]">
            <span className="h-2 w-2 rounded-full bg-[#f97316]" />
            <span>
              <span className="font-semibold text-[#0f172a]">Powered by Groq</span> for the one step that
              needs an LLM — grounded explanations, generated fast enough to stay inside the &lt;15s upload
              budget.
            </span>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#e7e1d4] px-6 py-10">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 text-sm text-[#94a3b8] sm:flex-row">
          <Wordmark className="opacity-80" />
          <p>Built for families managing correspondence across agencies that don’t talk to each other.</p>
        </div>
      </footer>
    </div>
  )
}
