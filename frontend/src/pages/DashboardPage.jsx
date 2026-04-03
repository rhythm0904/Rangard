// src/pages/DashboardPage.jsx
import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { useScansStore } from '../store/scansStore'
import { useAuthStore } from '../store/authStore'
import ThreatBadge from '../components/ThreatBadge'

const THREAT_COLORS = {
  critical: '#f85149',
  high:     '#fb923c',
  medium:   '#fbbf24',
  low:      '#60a5fa',
  clean:    '#3fb950',
}

const CARD_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  show:   { opacity: 1, y: 0 },
}

export default function DashboardPage() {
  const user       = useAuthStore((s) => s.user)
  const { scans, analytics, loading, fetchScans, fetchAnalytics } = useScansStore()

  useEffect(() => {
    fetchScans()
    fetchAnalytics()
  }, [])

  // Build pie chart data from analytics
  const pieData = analytics
    ? Object.entries(analytics.by_threat_level).map(([level, count]) => ({
        name:  level,
        value: count,
        color: THREAT_COLORS[level] || '#888',
      }))
    : []

  // Build 7-day area chart from scan timestamps
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return format(d, 'MMM d')
  })
  const areaData = last7Days.map((day) => ({
    day,
    scans: scans.filter((s) =>
      s.created_at && format(parseISO(s.created_at), 'MMM d') === day
    ).length,
    threats: scans.filter((s) =>
      s.created_at &&
      format(parseISO(s.created_at), 'MMM d') === day &&
      s.threat_level &&
      s.threat_level !== 'clean'
    ).length,
  }))

  const StatCard = ({ label, value, sub, color = 'violet', icon }) => (
    <motion.div variants={CARD_VARIANTS} className="glass p-5">
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl">{icon}</span>
        <span className={`text-3xl font-bold text-${color}-400`}>{value}</span>
      </div>
      <p className="text-sm font-medium text-[#c9d1d9]">{label}</p>
      {sub && <p className="text-xs text-[#8b949e] mt-0.5">{sub}</p>}
    </motion.div>
  )

  return (
    <div className="pt-16 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 py-8">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-bold text-[#c9d1d9]">
            Welcome back, {user?.full_name?.split(' ')[0] || 'there'} 👋
          </h1>
          <p className="text-[#8b949e] mt-1">
            Here's your security overview. Ready to{' '}
            <Link to="/upload" className="text-violet-400 hover:underline">scan a file</Link>?
          </p>
        </motion.div>

        {/* Stat cards */}
        <motion.div
          variants={{ show: { transition: { staggerChildren: 0.08 } } }}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          <StatCard
            icon="📁" label="Total scans"
            value={analytics?.total_scans ?? 0}
            sub="All time"
            color="violet"
          />
          <StatCard
            icon="✅" label="Clean files"
            value={analytics?.clean_count ?? 0}
            sub="No threats"
            color="green"
          />
          <StatCard
            icon="🚨" label="Quarantined"
            value={analytics?.quarantine_count ?? 0}
            sub="Isolated threats"
            color="red"
          />
          <StatCard
            icon="⛓️" label="Blockchain"
            value={scans.filter((s) => s.has_blockchain).length}
            sub="Anchored hashes"
            color="blue"
          />
        </motion.div>

        {/* Charts row */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">

          {/* Area chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass p-6 lg:col-span-2"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-4">
              Scan activity — last 7 days
            </h2>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={areaData}>
                <defs>
                  <linearGradient id="gScans" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#7c3aed" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#f85149" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f85149" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#30363d" strokeDasharray="3 3" />
                <XAxis dataKey="day" tick={{ fill: '#8b949e', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8b949e', fontSize: 11 }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }}
                  labelStyle={{ color: '#c9d1d9' }}
                />
                <Area type="monotone" dataKey="scans"   stroke="#7c3aed" fill="url(#gScans)"   strokeWidth={2} name="Total scans" />
                <Area type="monotone" dataKey="threats" stroke="#f85149" fill="url(#gThreats)" strokeWidth={2} name="Threats" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-3 text-xs text-[#8b949e]">
              <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-violet-500 inline-block" />Total scans</span>
              <span className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-red-500 inline-block" />Threats detected</span>
            </div>
          </motion.div>

          {/* Pie chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass p-6"
          >
            <h2 className="text-sm font-semibold text-[#c9d1d9] mb-4">
              Threat breakdown
            </h2>
            {pieData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%" cy="50%"
                      innerRadius={45} outerRadius={70}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} stroke="transparent" />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-1.5 mt-2">
                  {pieData.map((d, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                        <span className="text-[#8b949e] capitalize">{d.name}</span>
                      </span>
                      <span className="text-[#c9d1d9] font-medium">{d.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-40 text-[#484f58] text-sm">
                <span className="text-3xl mb-2">📊</span>
                No data yet — scan some files
              </div>
            )}
          </motion.div>
        </div>

        {/* Recent scans */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass"
        >
          <div className="flex items-center justify-between p-5 border-b border-surface-border">
            <h2 className="text-sm font-semibold text-[#c9d1d9]">Recent scans</h2>
            <Link to="/reports" className="text-xs text-violet-400 hover:underline">
              View all →
            </Link>
          </div>

          {loading ? (
            <div className="p-8 text-center text-[#8b949e] text-sm">Loading…</div>
          ) : scans.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-4xl mb-3">🔍</div>
              <p className="text-[#8b949e] mb-4">No files scanned yet</p>
              <Link to="/upload" className="btn-primary">Scan your first file →</Link>
            </div>
          ) : (
            <div className="divide-y divide-surface-border">
              {scans.slice(0, 8).map((scan) => (
                <Link
                  key={scan.id}
                  to={`/scans/${scan.id}`}
                  className="flex items-center justify-between px-5 py-3.5 hover:bg-surface-hover
                             transition-colors duration-150 group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-lg flex-shrink-0">
                      {scan.threat_level === 'clean' ? '✅' :
                       scan.threat_level === 'critical' ? '🔴' : '⚠️'}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm text-[#c9d1d9] font-medium truncate max-w-xs group-hover:text-violet-400 transition-colors">
                        {scan.filename}
                      </p>
                      <p className="text-xs text-[#484f58] mt-0.5">
                        {scan.created_at ? format(parseISO(scan.created_at), 'MMM d, yyyy · HH:mm') : '—'}
                        {scan.has_blockchain && <span className="ml-2 text-blue-500">⛓️ anchored</span>}
                        {scan.is_quarantined && <span className="ml-2 text-orange-500">🔒 quarantined</span>}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {scan.confidence != null && (
                      <span className="text-xs text-[#8b949e] font-mono">
                        {(scan.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                    <ThreatBadge level={scan.threat_level || 'clean'} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </motion.div>

      </div>
    </div>
  )
}
