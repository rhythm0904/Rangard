// src/App.jsx — RANGARD
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/authStore";

import Navbar from "./components/Navbar";
import RegisterPage from "./pages/RegisterPage";
import Dashboard from "./pages/DashboardPage";
import UploadPage from "./pages/UploadPage";
import Reports from "./pages/ReportsPage";

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/register" />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <Navbar />

      <Routes>
        {/* Default */}
        <Route path="/" element={<Navigate to="/register" />} />

        {/* Public */}
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <UploadPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
