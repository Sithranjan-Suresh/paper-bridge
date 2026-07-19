import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import LandingPage from './pages/LandingPage.jsx'
import CaseTimelinePage from './pages/CaseTimelinePage.jsx'
import DocumentDetailPage from './pages/DocumentDetailPage.jsx'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/case/:caseId" element={<CaseTimelinePage />} />
        <Route path="/document/:documentId" element={<DocumentDetailPage />} />
      </Routes>
    </>
  )
}

export default App
