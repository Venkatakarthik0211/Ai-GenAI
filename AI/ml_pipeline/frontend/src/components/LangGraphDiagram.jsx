import React, { useState, useEffect, useRef } from 'react'
import { pipelineApi } from '../services/api'
import mermaid from 'mermaid'

// Initialize mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
})

function LangGraphDiagram({ currentNode, completedNodes = [], failedNodes = [] }) {
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)
  const [mermaidCode, setMermaidCode] = useState('')
  const mermaidRef = useRef(null)

  const fetchGraph = async () => {
    setLoading(true)
    setError(false)
    try {
      const response = await fetch(pipelineApi.getGraphVisualization())
      if (!response.ok) throw new Error('Failed to fetch graph')
      const data = await response.json()
      setMermaidCode(data.mermaid)
    } catch (err) {
      console.error('Failed to load LangGraph visualization:', err)
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGraph()
  }, [])

  useEffect(() => {
    if (mermaidCode && mermaidRef.current) {
      // Clear previous diagram
      mermaidRef.current.innerHTML = ''

      // Render new diagram
      const renderDiagram = async () => {
        try {
          const id = `mermaid-${Date.now()}`
          const { svg } = await mermaid.render(id, mermaidCode)
          mermaidRef.current.innerHTML = svg
        } catch (err) {
          console.error('Failed to render mermaid diagram:', err)
          setError(true)
        }
      }

      renderDiagram()
    }
  }, [mermaidCode])

  const handleRefresh = () => {
    fetchGraph()
  }

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-2xl">🔀</span>
          LangGraph Pipeline State
        </h3>
        <button
          onClick={handleRefresh}
          className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded"
          title="Refresh visualization"
        >
          🔄 Refresh
        </button>
      </div>

      <div className="overflow-x-auto overflow-y-auto max-h-[600px] min-h-[400px] flex items-center justify-center bg-gray-900 rounded">
        {loading ? (
          <div className="text-center p-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-400 text-sm">Loading graph...</p>
          </div>
        ) : error ? (
          <div className="text-center p-8">
            <p className="text-red-400 text-sm mb-4">Failed to load graph visualization</p>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
            >
              🔄 Try Again
            </button>
          </div>
        ) : (
          <div ref={mermaidRef} className="w-full flex justify-center p-4"></div>
        )}
      </div>

      {/* Status Legend */}
      <div className="mt-4 p-3 bg-gray-900 rounded">
        <h4 className="text-xs font-semibold text-gray-400 mb-2 uppercase">Pipeline Status</h4>
        {currentNode && (
          <div className="text-sm text-white mb-1">
            <span className="font-semibold">Current Node:</span>{' '}
            <span className="text-blue-400 font-mono">{currentNode}</span>
          </div>
        )}
        <div className="grid grid-cols-2 gap-2 text-xs mt-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-300">Completed: {completedNodes.length}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-300">Failed: {failedNodes.length}</span>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-500 mt-2 italic">
        Showing the actual LangGraph state diagram generated from the backend workflow
      </p>
    </div>
  )
}

export default LangGraphDiagram
