import { useState, createContext } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import FleetOverview from './pages/FleetOverview'
import EngineAnalysis from './pages/EngineAnalysis'
import ModelPerformance from './pages/ModelPerformance'
import PredictData from './pages/PredictData'

export const AppContext = createContext()

const API_BASE = 'http://localhost:8000'

function App() {
  const [dataset, setDataset] = useState('FD001')
  const [windowSize, setWindowSize] = useState(30)
  const [useLlm, setUseLlm] = useState(true)

  return (
    <AppContext.Provider value={{ dataset, setDataset, windowSize, setWindowSize, useLlm, setUseLlm, API_BASE }}>
      <BrowserRouter>
        <div className="app-layout">
          <Navbar />
          <main className="main-content">
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/fleet" element={<FleetOverview />} />
                <Route path="/engine" element={<EngineAnalysis />} />
                <Route path="/performance" element={<ModelPerformance />} />
                <Route path="/predict" element={<PredictData />} />
              </Routes>
            </AnimatePresence>
          </main>
        </div>
      </BrowserRouter>
    </AppContext.Provider>
  )
}

export default App
