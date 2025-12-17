import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { PipelineProvider } from './context/PipelineContext'
import Home from './pages/Home'

function App() {
  return (
    <PipelineProvider>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </div>
    </PipelineProvider>
  )
}

export default App
