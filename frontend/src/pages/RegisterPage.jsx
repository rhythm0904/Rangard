// src/pages/RegisterPage.jsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'
import { authApi } from '../services/api'
import { useAuthStore } from '../store/authStore'

export default function RegisterPage() {
  const navigate = useNavigate()
  const setAuth  = useAuthStore((s) => s.setAuth)
  const [form, setForm]       = useState({ email: '', password: '', fullName: '' })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      const res = await authApi.register(form.email, form.password, form.fullName)
      setAuth(res.data.access_token, { email: form.email, full_name: form.fullName })
      toast.success('Account created! Welcome to RANGARD.')
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <span className="text-3xl">🛡️</span>
            <span className="text-xl font-bold gradient-text">RANGARD</span>
          </Link>
          <h1 className="text-2xl font-bold text-[#c9d1d9]">Create your free account</h1>
          <p className="text-[#8b949e] mt-1 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-violet-400 hover:underline">Sign in</Link>
          </p>
        </div>

        <div className="glass p-8 glow-purple">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-[#8b949e] mb-1.5">Full name</label>
              <input
                type="text"
                className="input"
                placeholder="Alice Smith"
                value={form.fullName}
                onChange={(e) => setForm({ ...form, fullName: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#8b949e] mb-1.5">Email address</label>
              <input
                type="email"
                required
                className="input"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#8b949e] mb-1.5">
                Password <span className="text-[#484f58] font-normal">(min 8 characters)</span>
              </label>
              <input
                type="password"
                required
                className="input"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>
            <motion.button
              type="submit"
              disabled={loading}
              whileTap={{ scale: 0.97 }}
              className="btn-primary w-full py-3 text-base"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating account…
                </span>
              ) : 'Create account →'}
            </motion.button>
          </form>

          <p className="text-xs text-[#484f58] text-center mt-5">
            By creating an account you agree to our{' '}
            <a href="/terms" className="text-violet-400 hover:underline">Terms of Service</a>
            {' '}and{' '}
            <a href="/privacy" className="text-violet-400 hover:underline">Privacy Policy</a>.
          </p>
        </div>
      </motion.div>
    </div>
  )
}
