export default function RiskBadge({ level }) {
  const cls = level === 'CRITICAL' ? 'critical' : level === 'MODERATE' ? 'moderate' : 'low'
  return (
    <span className={`risk-badge ${cls}`}>
      <span className="risk-dot" />
      {level}
    </span>
  )
}
