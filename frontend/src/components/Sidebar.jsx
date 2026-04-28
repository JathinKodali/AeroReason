import { useContext } from 'react'
import { NavLink } from 'react-router-dom'
import { AppContext } from '../App'
import { BarChart3, Search, TrendingUp, Upload, Plane, Bot } from 'lucide-react'

export default function Sidebar() {
  const { dataset, setDataset, windowSize, setWindowSize, useLlm, setUseLlm } = useContext(AppContext)

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Plane size={18} style={{ opacity: 0.6 }} />
          <div>
            <div className="logo-text">AeroReason</div>
            <div className="logo-sub">Predictive Maintenance</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Navigation</div>
        <NavLink to="/" end className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <BarChart3 size={16} />
          Fleet Overview
        </NavLink>
        <NavLink to="/engine" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <Search size={16} />
          Engine Analysis
        </NavLink>
        <NavLink to="/performance" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <TrendingUp size={16} />
          Model Performance
        </NavLink>
        <NavLink to="/predict" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <Upload size={16} />
          Predict
        </NavLink>
      </nav>

      <div className="sidebar-section-label">Configuration</div>
      <div className="sidebar-config">
        <div className="form-group">
          <label className="form-label">Dataset</label>
          <select className="form-select" value={dataset} onChange={e => setDataset(e.target.value)}>
            <option value="FD001">FD001</option>
            <option value="FD002">FD002</option>
            <option value="FD003">FD003</option>
            <option value="FD004">FD004</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Window Size</label>
          <select className="form-select" value={windowSize} onChange={e => setWindowSize(Number(e.target.value))}>
            {[10, 15, 20, 25, 30, 35, 40, 45, 50].map(w => (
              <option key={w} value={w}>{w} cycles</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>AI Reasoning</span>
            <span style={{ color: useLlm ? 'var(--text-primary)' : 'var(--text-tertiary)', cursor: 'pointer' }} onClick={() => setUseLlm(!useLlm)}>
              {useLlm ? 'ON' : 'OFF'}
            </span>
          </label>
          <button 
            className="btn-outline" 
            style={{ width: '100%', justifyContent: 'center', borderColor: useLlm ? 'transparent' : 'var(--border-subtle)', background: useLlm ? 'var(--bg-glass)' : 'transparent', color: useLlm ? 'var(--text-primary)' : 'var(--text-secondary)', marginTop: 2 }}
            onClick={() => setUseLlm(!useLlm)}
          >
            <Bot size={14} style={{ opacity: useLlm ? 1 : 0.5 }} />
            {useLlm ? 'Ollama Deep Analysis' : 'Rule-Based Fallback'}
          </button>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="model-status">
          <span className="status-dot online" />
          <span>NASA C-MAPSS Framework</span>
        </div>
      </div>
    </aside>
  )
}
