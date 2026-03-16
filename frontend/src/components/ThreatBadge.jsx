// src/components/ThreatBadge.jsx
const configs = {
  critical: { label: 'CRITICAL', cls: 'badge-critical', icon: '🔴' },
  high:     { label: 'HIGH',     cls: 'badge-high',     icon: '🟠' },
  medium:   { label: 'MEDIUM',   cls: 'badge-medium',   icon: '🟡' },
  low:      { label: 'LOW',      cls: 'badge-low',      icon: '🔵' },
  clean:    { label: 'CLEAN',    cls: 'badge-clean',    icon: '✅' },
}

export default function ThreatBadge({ level, size = 'sm' }) {
  const cfg = configs[level] || configs.clean
  const padding = size === 'lg' ? 'px-4 py-1.5 text-sm' : 'px-2.5 py-0.5 text-xs'
  return (
    <span className={`inline-flex items-center gap-1.5 font-mono font-semibold rounded-full ${padding} ${cfg.cls}`}>
      <span>{cfg.icon}</span>
      {cfg.label}
    </span>
  )
}
