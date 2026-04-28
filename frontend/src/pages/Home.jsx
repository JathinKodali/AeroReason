import { useContext, useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AppContext } from '../App'
import { BarChart3, Search, TrendingUp, Upload, ArrowRight, Activity } from 'lucide-react'
import PageWrapper from '../components/PageWrapper'

const features = [
  {
    icon: <BarChart3 size={20} />,
    title: 'Fleet Overview',
    desc: 'Monitor the full fleet with real-time RUL predictions, risk breakdowns, and interactive charts.',
    path: '/fleet',
    color: 'rgba(255,255,255,0.06)',
  },
  {
    icon: <Search size={20} />,
    title: 'Engine Analysis',
    desc: 'Deep-dive into individual engine health with AI-powered reasoning and sensor degradation trends.',
    path: '/engine',
    color: 'rgba(255,255,255,0.06)',
  },
  {
    icon: <TrendingUp size={20} />,
    title: 'Model Performance',
    desc: 'Evaluate LSTM prediction accuracy with scatter plots, error histograms, and RMSE metrics.',
    path: '/performance',
    color: 'rgba(255,255,255,0.06)',
  },
  {
    icon: <Upload size={20} />,
    title: 'Predict with Your Data',
    desc: 'Upload custom engine sensor CSV files and receive instant RUL predictions and maintenance insights.',
    path: '/predict',
    color: 'rgba(255,255,255,0.06)',
  },
]

export default function Home() {
  const { API_BASE } = useContext(AppContext)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/model/status`).then(r => r.json()).catch(() => null),
      fetch(`${API_BASE}/api/ollama/status`).then(r => r.json()).catch(() => null),
    ]).then(([model, ollama]) => {
      setStats({ model, ollama })
    })
  }, [API_BASE])

  return (
    <PageWrapper>
      {/* Animated background */}
      <div className="hero-bg">
        <motion.div
          className="orb orb-1"
          animate={{ x: [0, 80, -40, 0], y: [0, -60, 40, 0], scale: [1, 1.2, 0.9, 1] }}
          transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="orb orb-2"
          animate={{ x: [0, -70, 50, 0], y: [0, 50, -80, 0], scale: [1, 0.85, 1.15, 1] }}
          transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="orb orb-3"
          animate={{ x: [0, 60, -30, 0], y: [0, -40, 70, 0], scale: [1, 1.1, 0.95, 1] }}
          transition={{ duration: 25, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="orb orb-4"
          animate={{ x: [0, -50, 40, 0], y: [0, 30, -50, 0], scale: [1, 0.9, 1.1, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        <div className="grid-overlay" />
      </div>

      <div className="home-hero">
        <motion.div
          className="hero-content"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="hero-badge">
            <Activity size={12} />
            <span>NASA C-MAPSS Framework</span>
          </div>
          <h1 className="hero-title">
            Predictive<br />Maintenance
          </h1>
          <p className="hero-subtitle">
            Hybrid AI-powered remaining useful life prediction for turbofan engines. 
            Combining deep learning with intelligent reasoning for actionable maintenance decisions.
          </p>
          <div className="hero-stats">
            <div className="hero-stat">
              <span className="hero-stat-value">LSTM</span>
              <span className="hero-stat-label">Deep Learning</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-value">4</span>
              <span className="hero-stat-label">Datasets</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-value">{stats?.model?.model_exists ? '✓' : '—'}</span>
              <span className="hero-stat-label">Model Ready</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-value">{stats?.ollama?.online ? '✓' : '—'}</span>
              <span className="hero-stat-label">Ollama</span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="home-grid">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <Link to={f.path} className="home-card">
              <div className="home-card-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
              <div className="home-card-arrow">
                <ArrowRight size={14} />
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </PageWrapper>
  )
}
