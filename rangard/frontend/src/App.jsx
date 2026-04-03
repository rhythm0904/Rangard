// src/App.jsx — RANGARD
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Navbar from './components/Navbar'
import LandingPage    from './pages/LandingPage'
import LoginPage      from './pages/LoginPage'
import RegisterPage   from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import DashboardPage  from './pages/DashboardPage'
import UploadPage     from './pages/UploadPage'
import ReportsPage    from './pages/ReportsPage'
import ScanDetailPage from './pages/ScanDetailPage'

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore(s => s.isAuthenticated)
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <div style={{ minHeight: '100vh', background: '#04060f' }}>
      <Navbar />
      <Routes>
        <Route path="/"          element={<LandingPage />} />
        <Route path="/login"     element={<LoginPage />} />
        <Route path="/register"  element={<RegisterPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/upload"    element={<ProtectedRoute><UploadPage /></ProtectedRoute>} />
        <Route path="/reports"   element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
        <Route path="/scans/:id" element={<ProtectedRoute><ScanDetailPage /></ProtectedRoute>} />
        <Route path="*"          element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
