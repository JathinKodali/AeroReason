import { motion } from 'framer-motion'

export default function InsightCard({ label, icon, children, variant, delay = 0 }) {
  const cls = variant === 'CRITICAL' ? 'critical' : variant === 'MODERATE' ? 'moderate' : ''
  return (
    <motion.div
      className={`insight-card ${cls}`}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="insight-label">
        {icon && <span>{icon}</span>}
        {label}
      </div>
      <div className="insight-body">{children}</div>
    </motion.div>
  )
}
