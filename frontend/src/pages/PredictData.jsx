import { useState, useContext, useCallback } from 'react'
import { AppContext } from '../App'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, ChevronDown, ChevronUp } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'
import MetricCard from '../components/MetricCard'
import RiskBadge from '../components/RiskBadge'
import InsightCard from '../components/InsightCard'
import Loading from '../components/Loading'

export default function PredictData() {
  const { windowSize, useLlm, API_BASE } = useContext(AppContext)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [fileName, setFileName] = useState(null)
  const [expanded, setExpanded] = useState({})

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]
    setFileName(file.name)
    setError(null)
    setLoading(true)
    setResults(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/api/predict/upload?window=${windowSize}&use_llm=${useLlm}`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Prediction failed')
      } else {
        setResults(data)
        // Auto-expand critical engines
        const exp = {}
        data.results.forEach(r => {
          if (r.risk_level === 'CRITICAL') exp[r.engine_id] = true
        })
        setExpanded(exp)
      }
    } catch (err) {
      setError('Network error. Is the API server running?')
    }
    setLoading(false)
  }, [windowSize, useLlm, API_BASE])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
  })

  const toggleExpand = (id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <PageWrapper>
      <div className="page-header">
        <div className="page-label">Custom Prediction</div>
        <h1>Predict with Your Data</h1>
        <p className="page-description">
          Upload engine sensor data in C-MAPSS format to receive RUL predictions, risk assessments, and maintenance recommendations.
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div {...getRootProps()} className={`upload-zone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          <div className="upload-icon">
            <Upload size={32} strokeWidth={1.2} />
          </div>
          <h3>{isDragActive ? 'Drop your CSV file here' : 'Upload Engine Sensor Data'}</h3>
          <p>Drag & drop a CSV file, or click to browse. Must include engine_id, cycle, and sensor columns.</p>
          {fileName && (
            <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
              <FileText size={14} style={{ opacity: 0.4 }} />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{fileName}</span>
            </div>
          )}
        </div>
      </motion.div>

      {loading && <Loading message="Running predictions on your data" />}

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{
            marginTop: 24,
            padding: '16px 20px',
            background: 'var(--critical-dim)',
            border: '1px solid rgba(255,59,59,0.2)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--critical)',
            fontSize: '0.82rem',
          }}
        >
          {error}
        </motion.div>
      )}

      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="section-header" style={{ marginTop: 36 }}>
            <h2>Prediction Results</h2>
            <span className="section-sub">{results.rows_loaded.toLocaleString()} rows · {results.features_detected} features</span>
          </div>

          <div className="metrics-grid">
            <MetricCard label="Engines" value={results.total_engines} delay={0} />
            <MetricCard label="Avg RUL" value={results.avg_rul} unit="cycles" delay={0.05} />
            <MetricCard label="Critical" value={results.critical} delay={0.1} />
            <MetricCard label="Healthy" value={results.low} delay={0.15} />
          </div>

          <div className="data-table-container" style={{ marginBottom: 32 }}>
            <div className="table-header">
              <h3>Engine Results</h3>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Engine ID</th>
                  <th>Predicted RUL</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {results.results.map(r => (
                  <tr key={r.engine_id}>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>Engine {r.engine_id}</td>
                    <td>{r.predicted_rul} cycles</td>
                    <td><RiskBadge level={r.risk_level} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section-header">
            <h2>AI Reasoning & Recommendations</h2>
          </div>

          {results.results.map(r => (
            <div key={r.engine_id} className="expander">
              <div className="expander-header" onClick={() => toggleExpand(r.engine_id)}>
                <h3>
                  <RiskBadge level={r.risk_level} />
                  Engine {r.engine_id} — RUL: {r.predicted_rul} cycles
                </h3>
                {expanded[r.engine_id] ? <ChevronUp size={16} style={{ opacity: 0.4 }} /> : <ChevronDown size={16} style={{ opacity: 0.4 }} />}
              </div>
              <AnimatePresence>
                {expanded[r.engine_id] && (
                  <motion.div
                    className="expander-body"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                  >
                    <div className="two-col">
                      <InsightCard label="Explanation" icon="◆" variant={r.risk_level}>
                        {r.explanation}
                      </InsightCard>
                      <InsightCard label="Recommendation" icon="→" variant={r.risk_level}>
                        {r.recommendation.split('\n').map((line, i) => (
                          <div key={i} style={{ marginBottom: 4 }}>{line}</div>
                        ))}
                      </InsightCard>
                    </div>
                    {r.trend_summary && (
                      <InsightCard label="Degradation Trend" icon="↘">
                        {r.trend_summary}
                      </InsightCard>
                    )}

                    <div style={{ marginTop: 16 }}>
                      <p style={{ fontSize: '0.65rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: 8 }}>Data Sent to AI</p>
                      <pre style={{ 
                        background: 'var(--bg-secondary)', 
                        padding: '16px', 
                        borderRadius: 'var(--radius-sm)', 
                        fontSize: '0.7rem',
                        color: 'var(--text-tertiary)',
                        border: '1px solid var(--border-subtle)',
                        overflowX: 'auto',
                        whiteSpace: 'pre-wrap'
                      }}>
{`Engine ID: ${r.engine_id}
Predicted Remaining Useful Life (RUL): ${r.predicted_rul} cycles
Risk Classification: ${r.risk_level}
Sensor Trend Analysis: ${r.trend_summary}`}
                      </pre>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </motion.div>
      )}
    </PageWrapper>
  )
}
