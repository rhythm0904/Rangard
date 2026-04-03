// src/services/api.js
// ────────────────────
// All communication with the FastAPI backend lives here.
// Components never call fetch() directly — they use these functions.

import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000, // 60s — scans can take a while
})

// Attach JWT token to every request automatically
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Redirect to login if 401 (token expired)
api.interceptors.response.use(
  (res) => res,
  (err) => {
   
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email, password, fullName) =>
    api.post('/api/auth/register', { email, password, full_name: fullName }),

  login: (email, password) => {
    const form = new FormData()
    form.append('username', email) // FastAPI OAuth2 uses 'username'
    form.append('password', password)
    return api.post('/api/auth/login', form)
  },

  me: () => api.get('/api/auth/me'),
}

// ── Scans ─────────────────────────────────────────────────────────────────────

export const scansApi = {
  upload: (file, onProgress) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/scans/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress) {
          onProgress(Math.round((e.loaded / e.total) * 100))
        }
      },
    })
  },

  list: (limit = 50, offset = 0) =>
    api.get('/api/scans/', { params: { limit, offset } }),

  get: (scanId) => api.get(`/api/scans/${scanId}`),

  downloadReport: (scanId) =>
    api.get(`/api/scans/${scanId}/report`, { responseType: 'blob' }),

  release: (scanId) => api.post(`/api/scans/${scanId}/release`),

  analytics: () => api.get('/api/scans/analytics/summary'),
}

// ── Health ────────────────────────────────────────────────────────────────────

export const healthApi = {
  check: () => api.get('/health'),
}
