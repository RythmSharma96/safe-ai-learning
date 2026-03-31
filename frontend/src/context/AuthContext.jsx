import { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, signup as apiSignup, getMe } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token && !user) {
      getMe()
        .then((res) => {
          setUser(res.data)
          localStorage.setItem('user', JSON.stringify(res.data))
        })
        .catch(() => {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const loginUser = async (email, password) => {
    const tokenRes = await apiLogin({ email, password })
    localStorage.setItem('access_token', tokenRes.data.access)
    localStorage.setItem('refresh_token', tokenRes.data.refresh)
    const meRes = await getMe()
    setUser(meRes.data)
    localStorage.setItem('user', JSON.stringify(meRes.data))
    return meRes.data
  }

  const signupUser = async (data) => {
    await apiSignup(data)
    return loginUser(data.email, data.password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, signupUser, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
