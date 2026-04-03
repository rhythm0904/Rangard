// src/pages/UploadPage.jsx
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import { useScansStore } from '../store/scansStore'
import ProgressRing from '../components/ProgressRing'
import ThreatBadge from '../components/ThreatBadge'

const MAX_MB = 50
const SCAN_STEPS = [
  'Reading file bytes…',
  'Calculating SHA-256 fingerprint…',
  'Extracting entropy features…',
  'Analysing PE headers…',
  'Checking ransomware strings…',
  'Running RandomForest model…',
  'Anchoring hash to Ethereum…',
  'Finalising results…',
]

const THREAT_RING_COLORS = {
  critical: '#f85149',
  high:     '#fb923c',
  medium:   '#fbbf24',
  low:      '#60a5fa',
  clean:    '#3fb950',
}

export default function UploadPage() {
  const navigate   = useNavigate()
  const { uploadFile } = useScansStore()

  const [phase, setPhase]         = useState('idle')   // idle | scanning | done | error
  const [file, setFile]           = useState(null)
  const [progress, setProgress]   = useState(0)
  const [stepIdx, setStepIdx]     = useState(0)
  const [result, setResult]       = useState(null)
  const [errorMsg, setErrorMsg]   = useState('')

  const runScan = async (selectedFile) => {
    setFile(selectedFile)
    setPhase('scanning')
    setProgress(0)
    setStepIdx(0)

    // Animate through steps while the real scan runs in the background
    const stepInterval = setInterval(() => {
      setStepIdx((i) => {
        const next = i + 1
        setProgress(Math.min(Math.round((next / SCAN_STEPS.length) * 90), 90))
        if (next >= SCAN_STEPS.length - 1) clearInterval(stepInterval)
        return next
      })
    }, 400)

    try {
      const data = await uploadFile(selectedFile)
      clearInterval(stepInterval)
      setProgress(100)
      setResult(data)
      setPhase('done')

      if (data.threat_level === 'critical' || data.threat_level === 'high') {
        toast.error(`${data.threat_level.toUpperCase()} threat detected — file quarantined!`)
      } else if (data.threat_level === 'medium') {
        toast.error('Medium threat detected — check the results below.')
      } else {
        toast.success('Scan complete — file looks clean.')
      }
    } catch (err) {
      clearInterval(stepInterval)
      const msg = err.response?.data?.detail || 'Scan failed — please try again.'
      setErrorMsg(msg)
      setPhase('error')
      toast.error(msg)
    }
  }

  const onDrop = useCallback(async (accepted) => {
    const f = accepted[0]
    if (!f) return
    if (f.size > MAX_MB * 1024 * 1024) {
      toast.error(`File too large — maximum is ${MAX_MB} MB`)
      return
    }
    await runScan(f)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    disabled: phase === 'scanning',
  })

  const reset = () => {
    setPhase('idle'); setFile(null); setProgress(0)
    setStepIdx(0); setResult(null); setErrorMsg('')
  }

  const ringColor = result
    ? THREAT_RING_COLORS[result.threat_level] || '#7c3aed'
    : '#7c3aed'

  return (
    <div className="pt-16 min-h-screen">
      <div className="max-w-3xl mx-auto px-4 py-12">

        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <h1 className="text-3xl font-bold text-[#c9d1d9] mb-2">Scan a file</h1>
          <p className="text-[#8b949e]">
            Upload any file up to {MAX_MB} MB. AI analysis runs in under 50 ms.
          </p>
        </motion.div>

        <AnimatePresence mode="wait">

          {/* ── Idle: drop zone ── */}
          {phase === 'idle' && (
            <motion.div
              key="dropzone"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <div
                {...getRootProps()}
                className={`
                  relative glass rounded-2xl p-16 text-center cursor-pointer
                  border-2 border-dashed transition-all duration-300 select-none
                  ${isDragActive
                    ? 'border-violet-400 glow-purple bg-violet-500/5'
                    : 'border-surface-border hover:border-violet-500/50 hover:glow-purple'}
                `}
              >
                <input {...getInputProps()} />

                {/* Animated orbit rings when dragging */}
                {isDragActive && (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
                      className="absolute inset-0 rounded-2xl border border-violet-500/20"
                    />
                    <motion.div
                      animate={{ rotate: -360 }}
                      transition={{ repeat: Infinity, duration: 5, ease: 'linear' }}
                      className="absolute inset-4 rounded-2xl border border-blue-500/20"
                    />
                  </>
                )}

                <motion.div
                  animate={isDragActive ? { scale: 1.2, rotate: 5 } : { scale: 1 }}
                  className="text-6xl mb-6"
                >
                  {isDragActive ? '🎯' : '📁'}
                </motion.div>

                <p className="text-xl font-semibold text-[#c9d1d9] mb-2">
                  {isDragActive ? 'Release to scan' : 'Drop a file here'}
                </p>
                <p className="text-[#8b949e] text-sm mb-6">
                  or click to browse — any file type, up to {MAX_MB} MB
                </p>

                <motion.span
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="btn-primary inline-block"
                >
                  Choose file
                </motion.span>

                {/* Supported formats hint */}
                <p className="text-xs text-[#484f58] mt-6">
                  EXE · DLL · PDF · DOCX · XLSX · ZIP · JPG · PNG · and more
                </p>
              </div>
            </motion.div>
          )}

          {/* ── Scanning: animated progress ── */}
          {phase === 'scanning' && (
            <motion.div
              key="scanning"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="glass rounded-2xl p-12 text-center relative overflow-hidden"
            >
              {/* Scan line sweeping effect */}
              <div className="scan-line absolute inset-0 pointer-events-none" />

              <div className="flex justify-center mb-8">
                <ProgressRing percent={progress} size={140} stroke={10} color={ringColor} />
              </div>

              <h2 className="text-xl font-semibold text-[#c9d1d9] mb-2">
                Scanning{' '}
                <span className="text-violet-400">{file?.name}</span>
              </h2>

              <AnimatePresence mode="wait">
                <motion.p
                  key={stepIdx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.25 }}
                  className="text-[#8b949e] text-sm"
                >
                  {SCAN_STEPS[stepIdx] || 'Processing…'}
                </motion.p>
              </AnimatePresence>

              <div className="mt-8 flex gap-2 justify-center">
                {SCAN_STEPS.map((_, i) => (
                  <motion.span
                    key={i}
                    animate={{
                      background: i <= stepIdx ? '#7c3aed' : '#30363d',
                      scale: i === stepIdx ? 1.4 : 1,
                    }}
                    className="w-1.5 h-1.5 rounded-full"
                  />
                ))}
              </div>
            </motion.div>
          )}

          {/* ── Done: results ── */}
          {phase === 'done' && result && (
            <motion.div
              key="done"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              {/* Result hero card */}
              <div className={`glass rounded-2xl p-8 text-center
                ${result.threat_level === 'clean' ? 'glow-green' :
                  result.threat_level === 'critical' ? 'glow-red' :
                  result.threat_level === 'high' ? 'glow-red' : 'glow-purple'}`}
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
                  className="flex justify-center mb-4"
                >
                  <ProgressRing
                    percent={Math.round((result.confidence || 0) * 100)}
                    size={120}
                    stroke={9}
                    color={THREAT_RING_COLORS[result.threat_level] || '#7c3aed'}
                  />
                </motion.div>

                <ThreatBadge level={result.threat_level} size="lg" />

                <h2 className="text-xl font-semibold text-[#c9d1d9] mt-4 mb-1">
                  {result.message}
                </h2>
                <p className="text-sm text-[#8b949e]">
                  Confidence: {((result.confidence || 0) * 100).toFixed(1)}%
                </p>
              </div>

              {/* Meta row */}
              <div className="grid grid-cols-2 gap-3">
                <div className="glass p-4 text-center">
                  <p className="text-xs text-[#8b949e] mb-1">File</p>
                  <p className="text-sm text-[#c9d1d9] font-medium truncate">{file?.name}</p>
                </div>
                <div className="glass p-4 text-center">
                  <p className="text-xs text-[#8b949e] mb-1">Blockchain TX</p>
                  {result.blockchain_tx ? (
                    <a
                      href={`https://sepolia.etherscan.io/tx/${result.blockchain_tx}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:underline font-mono"
                    >
                      {result.blockchain_tx.slice(0, 10)}…
                    </a>
                  ) : (
                    <p className="text-sm text-[#484f58]">—</p>
                  )}
                </div>
              </div>

              {/* Quarantine notice */}
              {result.quarantined && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="glass border-l-4 border-red-500 p-4 glow-red"
                >
                  <p className="text-sm font-semibold text-red-400 mb-0.5">
                    🔒 File quarantined
                  </p>
                  <p className="text-xs text-[#8b949e]">
                    The file has been encrypted and isolated. Check your email for a detailed alert.
                    You can release it from the scan detail page if you believe it's a false positive.
                  </p>
                </motion.div>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => navigate(`/scans/${result.scan_id}`)}
                  className="btn-primary flex-1 py-3"
                >
                  View full report →
                </button>
                <button onClick={reset} className="btn-secondary flex-1 py-3">
                  Scan another file
                </button>
              </div>
            </motion.div>
          )}

          {/* ── Error ── */}
          {phase === 'error' && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass rounded-2xl p-12 text-center glow-red"
            >
              <div className="text-5xl mb-4">⚠️</div>
              <h2 className="text-xl font-semibold text-[#c9d1d9] mb-2">Scan failed</h2>
              <p className="text-[#8b949e] text-sm mb-6">{errorMsg}</p>
              <button onClick={reset} className="btn-primary">Try again</button>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  )
}
