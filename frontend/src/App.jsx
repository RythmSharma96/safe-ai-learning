import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ChatPage from './pages/ChatPage'
import FlaggedListPage from './pages/FlaggedListPage'
import FlaggedDetailPage from './pages/FlaggedDetailPage'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to={user.role === 'learner' ? '/' : '/flagged'} /> : <LoginPage />}
      />
      <Route
        path="/signup"
        element={user ? <Navigate to={user.role === 'learner' ? '/' : '/flagged'} /> : <SignupPage />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute allowedRoles={['learner']}>
            <ChatPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/flagged"
        element={
          <ProtectedRoute allowedRoles={['teacher', 'admin']}>
            <FlaggedListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/flagged/:id"
        element={
          <ProtectedRoute allowedRoles={['teacher', 'admin']}>
            <FlaggedDetailPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  )
}

export default App
