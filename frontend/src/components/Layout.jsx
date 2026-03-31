import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-xl font-bold text-blue-600">
              Jurneego
            </Link>
            {user?.role === 'learner' && (
              <Link to="/" className="text-gray-600 hover:text-gray-900">
                Chat
              </Link>
            )}
            {(user?.role === 'teacher' || user?.role === 'admin') && (
              <Link to="/flagged" className="text-gray-600 hover:text-gray-900">
                Flagged Conversations
              </Link>
            )}
          </div>
          {user && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500">
                {user.first_name || user.email}{' '}
                <span className="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded">
                  {user.role}
                </span>
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>
      <main>{children}</main>
    </div>
  )
}
