import { Route, Routes } from 'react-router-dom'
import LandingPage from './pages/LandingPage.jsx'
import CaseTimelinePage from './pages/CaseTimelinePage.jsx'
import DocumentDetailPage from './pages/DocumentDetailPage.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/case/:caseId" element={<CaseTimelinePage />} />
      <Route path="/document/:documentId" element={<DocumentDetailPage />} />
    </Routes>
  )
}

export default App
