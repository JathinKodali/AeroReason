import { useContext, useState, useRef, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { AppContext } from '../App'
import { Plane, BarChart3, Search, TrendingUp, Upload, Bot, ChevronDown, Settings } from 'lucide-react'

export default function Navbar() {
  const { dataset, setDataset, windowSize, setWindowSize, useLlm, setUseLlm } = useContext(AppContext)
  const [showConfig, setShowConfig] = useState(false)
  const dropRef = useRef(null)

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) setShowConfig(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <nav className="top-navbar">
      <div className="navbar-inner">
        {/* Left: Brand */}
        <NavLink to="/" className="navbar-brand">
          <Plane size={18} />
          <span className="brand-text">AeroReason</span>
        </NavLink>

        {/* Center: Nav Links */}
        <div className="navbar-links">
          <NavLink to="/fleet" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <BarChart3 size={14} />
            Fleet
          </NavLink>
          <NavLink to="/engine" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <Search size={14} />
            Engine
          </NavLink>
          <NavLink to="/performance" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <TrendingUp size={14} />
            Performance
          </NavLink>
          <NavLink to="/predict" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <Upload size={14} />
            Predict
          </NavLink>
        </div>

        {/* Right: Config */}
        <div className="navbar-actions" ref={dropRef}>
          <button
            className={`nav-pill config-toggle ${useLlm ? 'ai-active' : ''}`}
            onClick={() => setUseLlm(!useLlm)}
            title={useLlm ? 'AI Reasoning ON – Click to disable' : 'AI Reasoning OFF – Click to enable'}
          >
            <Bot size={14} />
            {useLlm ? 'AI On' : 'AI Off'}
          </button>

          <button
            className="nav-pill config-toggle"
            onClick={() => setShowConfig(!showConfig)}
          >
            <Settings size={14} />
            {dataset}
            <ChevronDown size={12} style={{ opacity: 0.4, marginLeft: 2 }} />
          </button>

          {showConfig && (
            <div className="config-dropdown">
              <div className="config-dropdown-section">
                <label className="config-label">Dataset</label>
                {['FD001', 'FD002', 'FD003', 'FD004'].map(d => (
                  <button
                    key={d}
                    className={`config-option ${dataset === d ? 'selected' : ''}`}
                    onClick={() => { setDataset(d); setShowConfig(false) }}
                  >
                    {d}
                  </button>
                ))}
              </div>
              <div className="config-dropdown-divider" />
              <div className="config-dropdown-section">
                <label className="config-label">Window Size</label>
                <div className="config-chips">
                  {[10, 20, 30, 40, 50].map(w => (
                    <button
                      key={w}
                      className={`config-chip ${windowSize === w ? 'selected' : ''}`}
                      onClick={() => { setWindowSize(w); setShowConfig(false) }}
                    >
                      {w}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
