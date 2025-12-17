import React, { createContext, useContext, useState, useCallback } from 'react'

const PipelineContext = createContext(null)

export const usePipeline = () => {
  const context = useContext(PipelineContext)
  if (!context) {
    throw new Error('usePipeline must be used within PipelineProvider')
  }
  return context
}

export const PipelineProvider = ({ children }) => {
  const [runs, setRuns] = useState([])
  const [selectedRun, setSelectedRun] = useState(null)
  const [creatingNewRun, setCreatingNewRun] = useState(false)
  const [loadingRuns, setLoadingRuns] = useState(false)

  const addRun = useCallback((run) => {
    setRuns((prevRuns) => [run, ...prevRuns])
  }, [])

  const updateRun = useCallback((runId, updates) => {
    setRuns((prevRuns) =>
      prevRuns.map((run) =>
        run.pipeline_run_id === runId ? { ...run, ...updates } : run
      )
    )
    if (selectedRun?.pipeline_run_id === runId) {
      setSelectedRun((prev) => ({ ...prev, ...updates }))
    }
  }, [selectedRun])

  const removeRun = useCallback((runId) => {
    setRuns((prevRuns) => prevRuns.filter((run) => run.pipeline_run_id !== runId))
    if (selectedRun?.pipeline_run_id === runId) {
      setSelectedRun(null)
    }
  }, [selectedRun])

  const value = {
    runs,
    setRuns,
    selectedRun,
    setSelectedRun,
    creatingNewRun,
    setCreatingNewRun,
    loadingRuns,
    setLoadingRuns,
    addRun,
    updateRun,
    removeRun,
  }

  return (
    <PipelineContext.Provider value={value}>
      {children}
    </PipelineContext.Provider>
  )
}
