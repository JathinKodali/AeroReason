import { useState, useEffect, useContext } from 'react'
import { AppContext } from '../App'
import { motion } from 'framer-motion'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, ReferenceLine,
} from 'recharts'
import PageWrapper from '../components/PageWrapper'
import MetricCard from '../components/MetricCard'
import Loading from '../components/Loading'

export default function ModelPerformance() {
  const { dataset, windowSize, API_BASE } = useContext(AppContext)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`${API_BASE}/api/performance?dataset=${dataset}&window=${windowSize}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [dataset, windowSize, API_BASE])

  if (loading) return <Loading message="Evaluating model performance" />
  if (!data) return <div className="loading-container">Failed to load data</div>

  const scatterData = data.scatter.actual.map((a, i) => ({
    actual: a,
    predicted: data.scatter.predicted[i],
  }))

  const histData = data.histogram.counts.map((count, i) => ({
    bin: `${data.histogram.bins[i]}`,
    binCenter: (data.histogram.bins[i] + data.histogram.bins[i + 1]) / 2,
    count,
  }))

  const maxRUL = Math.max(
    ...data.scatter.actual,
    ...data.scatter.predicted
  )

  return (
    <PageWrapper>
      <div className="page-header">
        <div className="page-label">Model Performance</div>
        <h1>Prediction Accuracy</h1>
        <p className="page-description">
          Comprehensive evaluation of the LSTM model's RUL prediction accuracy and error distribution.
        </p>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Test RMSE" value={data.rmse.toFixed(1)} unit="cycles" delay={0} />
        <MetricCard label="Mean Error" value={data.mean_error.toFixed(1)} unit="cycles" delay={0.05} />
        <MetricCard label="Std Error" value={data.std_error.toFixed(1)} unit="cycles" delay={0.1} />
        <MetricCard label="Engines Tested" value={data.engines_tested} delay={0.15} />
      </div>

      <motion.div
        className="charts-row"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <div className="chart-container">
          <div className="chart-title">Predicted vs Actual RUL</div>
          <ResponsiveContainer width="100%" height={380}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="actual"
                name="Actual RUL"
                tick={{ fontSize: 10 }}
                label={{ value: 'Actual RUL', position: 'bottom', offset: 0, style: { fill: 'rgba(255,255,255,0.3)', fontSize: 11 } }}
              />
              <YAxis
                dataKey="predicted"
                name="Predicted RUL"
                tick={{ fontSize: 10 }}
                label={{ value: 'Predicted RUL', angle: -90, position: 'left', offset: 10, style: { fill: 'rgba(255,255,255,0.3)', fontSize: 11 } }}
              />
              <ReferenceLine
                segment={[{ x: 0, y: 0 }, { x: maxRUL, y: maxRUL }]}
                stroke="rgba(255,59,59,0.4)"
                strokeDasharray="5 5"
                strokeWidth={1.5}
              />
              <Tooltip
                contentStyle={{
                  background: '#0a0c10',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: 8,
                  fontSize: '0.78rem',
                }}
              />
              <Scatter
                data={scatterData}
                fill="rgba(255,255,255,0.5)"
                fillOpacity={0.6}
                r={3}
                animationDuration={1200}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <div className="chart-title">Error Distribution</div>
          <ResponsiveContainer width="100%" height={380}>
            <BarChart data={histData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="bin" tick={{ fontSize: 9 }} interval={4} />
              <YAxis tick={{ fontSize: 10 }} />
              <ReferenceLine x="0" stroke="rgba(255,59,59,0.5)" strokeDasharray="4 4" />
              <Tooltip
                contentStyle={{
                  background: '#0a0c10',
                  border: '1px solid rgba(255,255,255,0.12)',
                  borderRadius: 8,
                  fontSize: '0.78rem',
                }}
              />
              <Bar dataKey="count" radius={[3, 3, 0, 0]} animationDuration={1000}>
                {histData.map((entry, i) => (
                  <Cell key={i} fill="rgba(255,255,255,0.35)" />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </PageWrapper>
  )
}
