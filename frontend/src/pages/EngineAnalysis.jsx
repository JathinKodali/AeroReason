import { useState, useEffect, useContext } from 'react'
import { AppContext } from '../App'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import PageWrapper from '../components/PageWrapper'
import MetricCard from '../components/MetricCard'
import RiskBadge from '../components/RiskBadge'
import InsightCard from '../components/InsightCard'
import Loading from '../components/Loading'
import { ChevronDown, ChevronUp } from 'lucide-react'

export default function EngineAnalysis() {
  const { dataset, windowSize, useLlm, API_BASE } = useContext(AppContext)
  const [engines, setEngines] = useState([])
  const [selectedEngine, setSelectedEngine] = useState(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showContext, setShowContext] = useState(false)

  // Fetch engine list
  useEffect(() => {
    fetch(`${API_BASE}/api/predictions?dataset=${dataset}&window=${windowSize}`)
      .then(r => r.json())
      .then(d => {
        const ids = d.fleet.map(e => e.engine_id)
        setEngines(ids)
        if (ids.length > 0 && !selectedEngine) setSelectedEngine(ids[0])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [dataset, windowSize, API_BASE])

  // Fetch engine details
  useEffect(() => {
    if (!selectedEngine) return
    setLoading(true)
    fetch(`${API_BASE}/api/engine/${selectedEngine}?dataset=${dataset}&window=${windowSize}&use_llm=${useLlm}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [selectedEngine, dataset, windowSize, useLlm, API_BASE])

  if (loading && !data) return <Loading message="Loading engine data" />

  return (
    <PageWrapper>
      <div className="page-header">
        <div className="page-label">Engine Analysis</div>
        <h1>Deep Engine Inspection</h1>
        <p className="page-description">
          Detailed health assessment with AI-powered reasoning, risk classification, and sensor degradation trends.
        </p>
      </div>

      <div className="engine-selector">
        <select
          className="form-select"
          value={selectedEngine || ''}
          onChange={e => setSelectedEngine(Number(e.target.value))}
        >
          {engines.map(id => (
            <option key={id} value={id}>Engine {id}</option>
          ))}
        </select>
        {data && <RiskBadge level={data.risk_level} />}
      </div>

      {loading ? <Loading /> : data && (
        <>
          <div className="metrics-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
            <MetricCard label="Predicted RUL" value={data.predicted_rul} unit="cycles" delay={0} />
            <MetricCard label="Actual RUL" value={data.actual_rul} unit="cycles" delay={0.05} />
            <MetricCard
              label="Prediction Error"
              value={(data.actual_rul - data.predicted_rul).toFixed(1)}
              unit="cycles"
              delay={0.1}
            />
          </div>

          <div className="two-col">
            <div>
              <InsightCard
                label="Explanation"
                icon="◆"
                variant={data.risk_level}
                delay={0.15}
              >
                {data.explanation}
              </InsightCard>
              {data.trend_summary && (
                <InsightCard label="Degradation Trend" icon="↘" delay={0.25}>
                  {data.trend_summary}
                </InsightCard>
              )}
            </div>
            <div>
              <InsightCard
                label="Recommendation"
                icon="→"
                variant={data.risk_level}
                delay={0.2}
              >
                {data.recommendation.split('\n').map((line, i) => (
                  <div key={i} style={{ marginBottom: 4 }}>{line}</div>
                ))}
              </InsightCard>
            </div>
          </div>

          <div style={{ marginTop: 24 }}>
            <div className="expander">
              <div className="expander-header" onClick={() => setShowContext(!showContext)}>
                <h3 style={{ fontSize: '0.75rem' }}>View AI Context Payload</h3>
                {showContext ? <ChevronUp size={16} style={{ opacity: 0.4 }} /> : <ChevronDown size={16} style={{ opacity: 0.4 }} />}
              </div>
              <AnimatePresence>
                {showContext && (
                  <motion.div
                    className="expander-body"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                  >
                    <pre style={{ 
                      background: 'var(--bg-secondary)', 
                      padding: '16px', 
                      borderRadius: 'var(--radius-sm)', 
                      fontSize: '0.7rem',
                      color: 'var(--text-tertiary)',
                      border: '1px solid var(--border-subtle)',
                      overflowX: 'auto',
                      whiteSpace: 'pre-wrap',
                      marginTop: '8px'
                    }}>
{`Engine ID: ${data.engine_id}
Predicted Remaining Useful Life (RUL): ${data.predicted_rul} cycles
Risk Classification: ${data.risk_level}
Sensor Trend Analysis: ${data.trend_summary}`}
                    </pre>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="section-header" style={{ marginTop: 48 }}>
            <h2>Sensor Degradation Trends</h2>
            <span className="section-sub">{data.sensors.length} sensors</span>
          </div>

          <motion.div
            className="sensor-grid"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {data.sensors.slice(0, 6).map(sensor => {
              const sensorInfo = data.sensor_data[sensor]
              if (!sensorInfo) return null
              const chartData = sensorInfo.cycles.map((c, i) => ({
                cycle: c,
                value: sensorInfo.values[i],
              }))
              return (
                <div className="chart-container" key={sensor}>
                  <div className="chart-title">{sensor.replace('_', ' ').toUpperCase()}</div>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                      <XAxis dataKey="cycle" tick={{ fontSize: 9 }} />
                      <YAxis tick={{ fontSize: 9 }} domain={['auto', 'auto']} />
                      <Tooltip
                        contentStyle={{
                          background: '#0a0c10',
                          border: '1px solid rgba(255,255,255,0.12)',
                          borderRadius: 8,
                          fontSize: '0.75rem',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="rgba(255,255,255,0.5)"
                        strokeWidth={1.5}
                        dot={false}
                        animationDuration={1000}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )
            })}
          </motion.div>
        </>
      )}
    </PageWrapper>
  )
}
