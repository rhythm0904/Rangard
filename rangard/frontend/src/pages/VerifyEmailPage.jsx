// src/pages/VerifyEmailPage.jsx
import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'
import { authApi } from '../services/api'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  const [loading, setLoading] = useState(false)
  const [verified, setVerified] = useState(false)
  const [email, setEmail] = useState('')

  useEffect(() => {
    if (token) {
      verifyEmail()
    }
  }, [token])

  const verifyEmail = async () => {
    if (!token) return
    setLoading(true)
    try {
      const res = await authApi.verifyEmail(token)
      setEmail(res.data.email)
      setVerified(true)
      toast.success('✅ Email verified successfully!')
      
      // Redirect to dashboard after 3 seconds
      setTimeout(() => {
        navigate('/dashboard')
      }, 3000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Verification failed')
      setVerified(false)
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
          <h1 className="text-2xl font-bold text-[#c9d1d9]">Verify Your Email</h1>
          <p className="text-[#8b949e] mt-2 text-sm">
            Click the button below to verify your email address
          </p>
        </div>

        <div className="glass p-8 glow-purple">
          {!token ? (
            <div className="space-y-6">
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                <p className="text-yellow-200 text-sm">
                  ⚠️ No verification link found. 
                </p>
                <p className="text-[#8b949e] text-sm mt-2">
                  Paste the verification link from your email into your browser's address bar.
                </p>
              </div>
            </div>
          ) : loading ? (
            <div className="space-y-6 text-center">
              <div className="flex justify-center">
                <div className="w-12 h-12 border-4 border-violet-500/30 border-t-violet-500 rounded-full animate-spin" />
              </div>
              <p className="text-[#8b949e]">Verifying your email...</p>
            </div>
          ) : verified ? (
            <div className="space-y-6">
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 text-center">
                <p className="text-3xl mb-2">✅</p>
                <p className="text-green-200 font-medium">Email verified!</p>
                <p className="text-[#8b949e] text-sm mt-2">
                  Your email <strong>{email}</strong> has been verified.
                </p>
              </div>
              
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                <p className="text-blue-200 text-sm">
                  🎉 You can now receive threat alert emails!
                </p>
                <p className="text-[#8b949e] text-xs mt-2">
                  Redirecting you to dashboard in a moment...
                </p>
              </div>

              <motion.button
                onClick={() => navigate('/dashboard')}
                whileTap={{ scale: 0.97 }}
                className="btn-primary w-full py-3"
              >
                Go to Dashboard →
              </motion.button>
            </div>
          ) : (
            <div className="space-y-4 text-red-400">
              <p className="text-sm">❌ Verification failed</p>
              <p className="text-xs text-[#8b949e]">
                The link may have expired. Request a new verification email.
              </p>
            </div>
          )}

          {!token && (
            <motion.button
              onClick={() => navigate('/dashboard')}
              whileTap={{ scale: 0.97 }}
              className="btn-primary w-full py-3 mt-6"
            >
              Back to Dashboard
            </motion.button>
          )}
        </div>
      </motion.div>
    </div>
  )
}
