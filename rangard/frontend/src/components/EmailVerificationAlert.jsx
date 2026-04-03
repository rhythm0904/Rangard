// src/components/EmailVerificationAlert.jsx
import { useState } from 'react'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'
import { authApi } from '../services/api'

export default function EmailVerificationAlert({ email, onVerified }) {
  const [loading, setLoading] = useState(false)

  const handleResend = async () => {
    setLoading(true)
    try {
      await authApi.resendVerification()
      toast.success(`✉️ Verification email sent to ${email}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to resend email')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass glow-yellow border-l-4 border-yellow-500 p-4 mb-6 rounded-lg"
    >
      <div className="flex items-start gap-4">
        <div className="text-2xl flex-shrink-0 mt-1">📧</div>
        <div className="flex-1 min-w-0">
          <h3 className="text-yellow-200 font-semibold mb-1">Email Verification Required</h3>
          <p className="text-[#8b949e] text-sm mb-3">
            Verify your email address to receive threat alerts when suspicious files are detected. 
            Check your inbox for a verification link, or request a new one below.
          </p>
          <div className="flex gap-3 flex-wrap">
            <motion.button
              onClick={handleResend}
              disabled={loading}
              whileTap={{ scale: 0.95 }}
              className="px-4 py-2 bg-yellow-600/30 hover:bg-yellow-600/50 border border-yellow-500/50 rounded-lg text-yellow-200 text-sm font-medium transition-colors"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-3 h-3 border border-yellow-200/50 border-t-yellow-200 rounded-full animate-spin" />
                  Sending...
                </span>
              ) : (
                '📨 Resend Verification Email'
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
