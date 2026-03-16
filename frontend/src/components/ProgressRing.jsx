// src/components/ProgressRing.jsx
// Circular progress indicator used during scans.

export default function ProgressRing({ percent = 0, size = 120, stroke = 8, color = '#7c3aed' }) {
  const r      = (size - stroke) / 2
  const circ   = 2 * Math.PI * r
  const offset = circ - (percent / 100) * circ

  return (
    <svg width={size} height={size} className="drop-shadow-lg">
      {/* Track */}
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none"
        stroke="#30363d"
        strokeWidth={stroke}
      />
      {/* Progress */}
      <circle
        cx={size / 2} cy={size / 2} r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        className="progress-ring-circle"
        style={{ filter: `drop-shadow(0 0 6px ${color})` }}
      />
      {/* Label */}
      <text
        x="50%" y="50%"
        textAnchor="middle" dominantBaseline="central"
        fill="white" fontSize={size / 5} fontWeight="600"
        fontFamily="Inter, sans-serif"
      >
        {percent}%
      </text>
    </svg>
  )
}
