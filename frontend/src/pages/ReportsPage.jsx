// src/pages/ReportsPage.jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { format, parseISO } from 'date-fns'
import { toast } from 'react-hot-toast'
import { useScansStore } from '../store/scansStore'
import ThreatBadge from '../components/ThreatBadge'

const THREAT_LEVELS = ['all', 'critical', 'high', 'medium', 'low', 'clean']

export default function ReportsPage() {
  const { scans, loading, fetchScans, downloadReport } = useScansStore()
  const [filterLevel, setFilterLevel]   = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [search, setSearch]             = useState('')
  const [downloading, setDownloading]   = useState(null)

  useEffect(() => { fetchScans() }, [])

  const filtered = scans.filter((s) => {
    if (filterLevel !== 'all' && s.threat_level !== filterLevel) return false
    if (filterStatus === 'quarantined' && !s.is_quarantined) return false
    if (filterStatus === 'blockchain' && !s.has_blockchain) return false
    if (search && !s.filename?.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const handleDownload = async (scanId, filename) => {
    setDownloading(scanId)
    try {
      await downloadReport(scanId, filename)
      toast.success('PDF report downloaded')
    } catch {
      toast.error('Could not generate report')
    } finally {
      setDownloading(null)
    }
  }

  return (
    <div className="pt-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-2xl font-bold text-[#c9d1d9]">Scan Reports</h1>
            <p className="text-[#8b949e] mt-1 text-sm">
              {scans.length} total scan{scans.length !== 1 ? 's' : ''}
            </p>
          </div>
          <Link to="/upload" className="btn-primary">
            + Scan new file
          </Link>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass p-4 mb-6 flex flex-wrap gap-3 items-center"
        >
          {/* Search */}
          <input
            type="text"
            placeholder="Search filename…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input flex-1 min-w-48 py-2 text-sm"
          />

          {/* Threat level filter */}
          <div className="flex gap-1.5 flex-wrap">
            {THREAT_LEVELS.map((l) => (
              <button
                key={l}
                onClick={() => setFilterLevel(l)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all duration-150
                  ${filterLevel === l
                    ? 'bg-violet-600 text-white'
                    : 'bg-surface-hover text-[#8b949e] hover:text-[#c9d1d9]'}`}
              >
                {l}
              </button>
            ))}
          </div>

          {/* Status filter */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input py-2 text-sm w-auto"
          >
            <option value="all">All statuses</option>
            <option value="quarantined">Quarantined</option>
            <option value="blockchain">Blockchain anchored</option>
          </select>
        </motion.div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass overflow-hidden"
        >
          {/* Table header */}
          <div className="hidden md:grid grid-cols-12 gap-4 px-5 py-3 border-b border-surface-border
                          text-xs font-medium text-[#8b949e] uppercase tracking-wider">
            <span className="col-span-4">File</span>
            <span className="col-span-2">Threat</span>
            <span className="col-span-2">Confidence</span>
            <span className="col-span-2">Date</span>
            <span className="col-span-2 text-right">Actions</span>
          </div>

          {loading ? (
            <div className="p-10 text-center text-[#8b949e] text-sm">
              <span className="inline-block w-5 h-5 border-2 border-violet-500/40 border-t-violet-500 rounded-full animate-spin mr-2 align-middle" />
              Loading…
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-4xl mb-3">📂</div>
              <p className="text-[#8b949e]">No scans match your filters</p>
            </div>
          ) : (
            <div className="divide-y divide-surface-border">
              {filtered.map((scan, i) => (
                <motion.div
                  key={scan.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="grid grid-cols-12 gap-4 px-5 py-4 hover:bg-surface-hover
                             transition-colors duration-150 items-center"
                >
                  {/* Filename */}
                  <div className="col-span-12 md:col-span-4 min-w-0">
                    <Link
                      to={`/scans/${scan.id}`}
                      className="text-sm text-[#c9d1d9] hover:text-violet-400 transition-colors font-medium truncate block"
                    >
                      {scan.filename}
                    </Link>
                    <div className="flex gap-2 mt-0.5">
                      {scan.is_quarantined && (
                        <span className="text-xs text-orange-400">🔒 quarantined</span>
                      )}
                      {scan.has_blockchain && (
                        <span className="text-xs text-blue-400">⛓️ anchored</span>
                      )}
                    </div>
                  </div>

                  {/* Threat */}
                  <div className="col-span-6 md:col-span-2">
                    <ThreatBadge level={scan.threat_level || 'clean'} />
                  </div>

                  {/* Confidence */}
                  <div className="col-span-6 md:col-span-2">
                    {scan.confidence != null ? (
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-surface-border rounded-full h-1.5 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-violet-500 transition-all duration-500"
                            style={{ width: `${scan.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-[#8b949e] w-8 text-right">
                          {(scan.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs text-[#484f58]">—</span>
                    )}
                  </div>

                  {/* Date */}
                  <div className="col-span-6 md:col-span-2 text-xs text-[#8b949e]">
                    {scan.created_at
                      ? format(parseISO(scan.created_at), 'MMM d, yyyy')
                      : '—'}
                  </div>

                  {/* Actions */}
                  <div className="col-span-6 md:col-span-2 flex gap-2 justify-end">
                    <Link
                      to={`/scans/${scan.id}`}
                      className="text-xs px-3 py-1.5 rounded-lg bg-surface-hover hover:bg-surface-border
                                 text-[#c9d1d9] transition-colors"
                    >
                      View
                    </Link>
                    {scan.status === 'complete' && (
                      <button
                        onClick={() => handleDownload(scan.id, scan.filename)}
                        disabled={downloading === scan.id}
                        className="text-xs px-3 py-1.5 rounded-lg bg-violet-600/20 hover:bg-violet-600/30
                                   text-violet-400 transition-colors disabled:opacity-50"
                      >
                        {downloading === scan.id ? '…' : 'PDF'}
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Summary footer */}
        {filtered.length > 0 && (
          <p className="text-xs text-[#484f58] text-center mt-4">
            Showing {filtered.length} of {scans.length} scan{scans.length !== 1 ? 's' : ''}
          </p>
        )}
      </div>
    </div>
  )
}
