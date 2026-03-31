import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({ baseURL: API_BASE })

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 by clearing tokens
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth
export const signup = (data) => api.post('/auth/signup/', data)
export const login = (data) => api.post('/auth/login/', data)
export const getMe = () => api.get('/auth/me/')

// Conversations
export const createConversation = (data) => api.post('/conversations/', data)
export const listConversations = () => api.get('/conversations/')
export const getConversation = (id) => api.get(`/conversations/${id}/`)
export const sendMessage = (conversationId, content) =>
  api.post(`/conversations/${conversationId}/messages/`, { content })

// Flagged (teacher/admin)
export const listFlaggedConversations = () => api.get('/conversations/flagged/')
export const getFlaggedConversation = (id) => api.get(`/conversations/flagged/${id}/`)

export default api
