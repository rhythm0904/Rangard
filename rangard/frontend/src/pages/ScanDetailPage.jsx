// src/pages/ScanDetailPage.jsx
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { format, parseISO } from 'date-fns'
import { toast } from 'react-hot-toast'
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer, Tooltip,
} from 'recharts'
import { scansApi } from '../services/api'
import { useScansStore } from '../store/scansStore'
import ThreatBadge from '../components/ThreatBadge'
import ProgressRing from '../components/ProgressRing'

const THREAT_RING = {
  critical: '#f85149', high: '#fb923c',
  medium: '#fbbf24', low: '#60a5fa', clean: '#3fb950',
}

export default function ScanDetailPage() {
  const { id }   = useParams()
  const { downloadReport } = useScansStore()
  const [scan, setScan]           = useState(null)
  const [loading, setLoading]     = useState(true)
  const [releasing, setReleasing] = useState(false)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    scansApi.get(id)
      .then((r) => setScan(r.data))
      .catch(() => toast.error('Could not load scan'))
      .finally(() => setLoading(false))
  }, [id])

  const handleRelease = async () => {
    if (!confirm('Release this file from quarantine? Only do this if you are certain it is safe.')) return
    setReleasing(true)
    try {
      await scansApi.release(id)
      setScan((s) => ({ ...s, is_quarantined: false }))
      toast.success('File released from quarantine')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Release failed')
    } finally {
      setReleasing(false)
    }
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      await downloadReport(id, scan.filename)
      toast.success('PDF report downloaded')
    } catch {
      toast.error('Could not generate report')
    } finally {
      setDownloading(false)
    }
  }

  // Build radar chart data from ml_features
  const radarData = scan?.ml_features ? [
    { subject: 'Entropy',     value: Math.round((scan.ml_features.entropy_full || 0) / 8 * 100) },
    { subject: 'Null bytes',  value: Math.round((scan.ml_features.null_byte_ratio || 0) * 100) },
    { subject: 'Ransom str.', value: Math.min(scan.ml_features.ransom_string_hits * 25, 100) },
    { subject: 'PE flags',    value: scan.ml_features.pe_suspicious ? 80 : scan.ml_features.is_pe ? 30 : 0 },
    { subject: 'Risk score',  value: Math.round((scan.confidence || 0) * 100) },
    { subject: 'Non-print',  value: Math.round((1 - (scan.ml_features.printable_ratio || 1)) * 100) },
  ] : []

  if (loading) {
    return (
      <div className="pt-16 min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-violet-500/40 border-t-violet-500 rounded-full animate-spin" />
      </div>
    )
  }

  if (!scan) {
    return (
      <div className="pt-16 min-h-screen flex flex-col items-center justify-center gap-4">
        <span className="text-4xl">🔍</span>
        <p className="text-[#8b949e]">Scan not found</p>
        <Link to="/reports" className="btn-secondary">← Back to reports</Link>
      </div>
    )
  }

  const threatColor = THREAT_RING[scan.threat_level] || '#7c3aed'

  return (
    <div className="pt-16 min-h-screen">
      <div className="max-w-5xl mx-auto px-4 py-8">

        {/* Back */}
        <Link to="/reports" className="text-sm text-[#8b949e] hover:text-violet-400 transition-colors flex items-center gap-1 mb-6">
          ← Back to reports
        </Link>

        {/* Header card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-6 mb-6 flex flex-col md:flex-row md:items-center gap-6"
          style={{ boxShadow: `0 0 30px ${threatColor}22` }}
        >
          <ProgressRing
            percent={Math.round((scan.confidence || 0) * 100)}
            size={110}
            stroke={9}
            color={threatColor}
          />
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-[#c9d1d9] truncate mb-2">
              {scan.filename}
            </h1>
            <div className="flex flex-wrap gap-2 mb-3">
              <ThreatBadge level={scan.threat_level || 'clean'} size="lg" />
              {scan.is_quarantined && (
                <span className="badge-medium px-3 py-1 text-xs rounded-full font-medium">
                  🔒 Quarantined
                </span>
              )}
              {scan.blockchain_tx && (
                <span className="bg-blue-900/30 text-blue-400 border border-blue-800/50 px-3 py-1 text-xs rounded-full font-medium">
                  ⛓️ On-chain
                </span>
              )}
            </div>
            <p className="text-sm text-[#8b949e]">
              Scanned {scan.completed_at
                ? format(parseISO(scan.completed_at), 'MMMM d, yyyy · HH:mm:ss') : '—'}
              {scan.scan_duration_ms != null && (
                <span className="ml-2 text-[#484f58]">({scan.scan_duration_ms} ms)</span>
              )}
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button onClick={handleDownload} disabled={downloading} className="btn-secondary text-sm">
              {downloading ? '…' : '⬇ PDF'}
            </button>
            {scan.is_quarantined && (
              <button onClick={handleRelease} disabled={releasing} className="btn-danger text-sm">
                {releasing ? '…' : '🔓 Release'}
              </button>
            )}
          </div>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">

          {/* File metadata */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass p-5"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-4">File information</h2>
            <table className="w-full text-sm">
              <tbody className="divide-y divide-surface-border">
                {[
                  ['Size',       scan.file_size_bytes != null ? `${scan.file_size_bytes.toLocaleString()} bytes` : '—'],
                  ['Type',       scan.mime_type || '—'],
                  ['SHA-256',    null],
                  ['Status',     scan.status],
                ].map(([k, v]) => (
                  <tr key={k}>
                    <td className="py-2.5 pr-4 text-[#8b949e] font-medium whitespace-nowrap">{k}</td>
                    <td className="py-2.5 text-[#c9d1d9] font-mono text-xs break-all">
                      {k === 'SHA-256'
                        ? <span className="text-[10px]">{scan.sha256}</span>
                        : v}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>

          {/* Radar chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="glass p-5"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-2">Threat feature analysis</h2>
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#30363d" />
                  <PolarAngleAxis dataKey="subject" tick={{ fill: '#8b949e', fontSize: 11 }} />
                  <Radar dataKey="value" stroke={threatColor} fill={threatColor} fillOpacity={0.2} strokeWidth={2} />
                  <Tooltip
                    contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }}
                    formatter={(v) => [`${v}%`, 'Score']}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-40 text-[#484f58] text-sm">No feature data</div>
            )}
          </motion.div>
        </div>

        {/* Detected patterns */}
        {scan.detected_patterns?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass p-5 mb-6"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-3">Detected patterns</h2>
            <ul className="space-y-2">
              {scan.detected_patterns.map((p, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + i * 0.05 }}
                  className="flex items-start gap-3 text-sm"
                >
                  <span className="text-red-400 mt-0.5 flex-shrink-0">⚠</span>
                  <span className="text-[#c9d1d9]">{p}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Technical features */}
        {scan.ml_features && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="glass p-5 mb-6"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-4">Technical features</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {[
                ['File entropy',      `${(scan.ml_features.entropy_full || 0).toFixed(3)} / 8.0`],
                ['Header entropy',    `${(scan.ml_features.entropy_header || 0).toFixed(3)} / 8.0`],
                ['PE executable',     scan.ml_features.is_pe ? 'Yes' : 'No'],
                ['PE sections',       scan.ml_features.pe_section_count ?? '—'],
                ['Ransom strings',    scan.ml_features.ransom_string_hits ?? 0],
                ['Printable bytes',   `${((scan.ml_features.printable_ratio || 0) * 100).toFixed(1)}%`],
                ['Null byte ratio',   `${((scan.ml_features.null_byte_ratio || 0) * 100).toFixed(1)}%`],
                ['High entropy',      scan.ml_features.high_entropy ? 'Yes ⚠' : 'No'],
              ].map(([label, val]) => (
                <div key={label} className="bg-surface-hover rounded-lg p-3">
                  <p className="text-xs text-[#8b949e] mb-0.5">{label}</p>
                  <p className="text-sm font-mono text-[#c9d1d9] font-medium">{val}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Blockchain proof */}
        {scan.blockchain_tx && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass p-5 glow-blue"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-4">⛓️ Blockchain proof</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-[#8b949e] mb-1">Transaction hash</p>
                <a
                  href={`https://sepolia.etherscan.io/tx/${scan.blockchain_tx}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs font-mono text-blue-400 hover:underline break-all"
                >
                  {scan.blockchain_tx}
                </a>
              </div>
              <div>
                <p className="text-xs text-[#8b949e] mb-1">What this means</p>
                <p className="text-xs text-[#8b949e] leading-relaxed">
                  This file's SHA-256 hash has been permanently recorded on the Ethereum Sepolia
                  blockchain. Anyone can verify the file has not been tampered with by recomputing
                  its hash and checking it against this transaction.
                </p>
              </div>
            </div>
          </motion.div>
        )}

      </div>
    </div>
  )
}
