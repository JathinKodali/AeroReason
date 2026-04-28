import { useState, useEffect, useContext } from 'react'
import { AppContext } from '../App'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import PageWrapper from '../components/PageWrapper'
import MetricCard from '../components/MetricCard'
import RiskBadge from '../components/RiskBadge'
import Loading from '../components/Loading'

const RISK_COLORS = { CRITICAL: '#ff3b3b', MODERATE: '#ff9f0a', LOW: '#30d158' }

export default function FleetOverview() {
  const { dataset, windowSize, API_BASE } = useContext(AppContext)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`${API_BASE}/api/predictions?dataset=${dataset}&window=${windowSize}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [dataset, windowSize, API_BASE])

  if (loading) return <Loading message="Running fleet predictions" />
  if (!data) return <div className="loading-container">Failed to load data</div>

  const barData = data.fleet.map(e => ({
    name: `E${e.engine_id}`,
    rul: e.predicted_rul,
    fill: RISK_COLORS[e.risk_level],
  }))

  const pieData = [
    { name: 'Critical', value: data.critical, color: RISK_COLORS.CRITICAL },
    { name: 'Moderate', value: data.moderate, color: RISK_COLORS.MODERATE },
    { name: 'Low Risk', value: data.low, color: RISK_COLORS.LOW },
  ].filter(d => d.value > 0)

  return (
    <PageWrapper>
      <div className="page-header">
        <div className="page-label">Fleet Overview</div>
        <h1>Engine Fleet Status</h1>
        <p className="page-description">
          Real-time RUL predictions and risk classification across all engines in the {dataset} dataset.
        </p>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Total Engines" value={data.total_engines} delay={0} />
        <MetricCard label="RMSE" value={data.rmse.toFixed(1)} unit="cycles" delay={0.05} />
        <MetricCard label="Critical" value={data.critical} delay={0.1} />
        <MetricCard label="Moderate" value={data.moderate} delay={0.15} />
      </div>

      <motion.div
        className="charts-row"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <div className="chart-container">
          <div className="chart-title">Predicted RUL per Engine</div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={barData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" tick={{ fontSize: 9 }} interval={Math.floor(barData.length / 20)} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: '#0a0c10',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: 8,
                  fontSize: '0.78rem',
                }}
              />
              <Bar dataKey="rul" radius={[3, 3, 0, 0]} animationDuration={1200}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <div className="chart-title">Risk Distribution</div>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={3}
                dataKey="value"
                animationDuration={1000}
                stroke="none"
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} fillOpacity={0.9} />
                ))}
              </Pie>
              <Legend
                verticalAlign="bottom"
                formatter={(value) => <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.72rem' }}>{value}</span>}
              />
              <Tooltip
                contentStyle={{
                  background: '#0a0c10',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: 8,
                  fontSize: '0.78rem',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35, duration: 0.5 }}
      >
        <div className="data-table-container">
          <div className="table-header">
            <h3>Fleet Status Table</h3>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              {data.fleet.length} engines
            </span>
          </div>
          <div style={{ maxHeight: 420, overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Engine ID</th>
                  <th>Predicted RUL</th>
                  <th>Actual RUL</th>
                  <th>Error</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {data.fleet.map(e => (
                  <tr key={e.engine_id}>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                      Engine {e.engine_id}
                    </td>
                    <td>{e.predicted_rul}</td>
                    <td>{e.actual_rul}</td>
                    <td style={{ color: e.error > 0 ? 'var(--low)' : e.error < -20 ? 'var(--critical)' : 'var(--text-secondary)' }}>
                      {e.error > 0 ? '+' : ''}{e.error}
                    </td>
                    <td><RiskBadge level={e.risk_level} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </motion.div>
    </PageWrapper>
  )
}
