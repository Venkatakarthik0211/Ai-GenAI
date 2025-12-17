import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { usePipeline } from '../context/PipelineContext'
import { pipelineApi } from '../services/api'
import LangGraphDiagram from '../components/LangGraphDiagram'
import AlgorithmSelectionForm from '../components/AlgorithmSelectionForm'
import ReviewForm from '../components/ReviewForm'
import PreprocessingReviewForm from '../components/PreprocessingReviewForm'

function Home() {
  const {
    runs,
    setRuns,
    selectedRun,
    setSelectedRun,
    creatingNewRun,
    setCreatingNewRun,
    loadingRuns,
    setLoadingRuns
  } = usePipeline()

  const [submittingPipeline, setSubmittingPipeline] = useState(false)
  const [pipelineError, setPipelineError] = useState(null)
  const [showRetryDialog, setShowRetryDialog] = useState(false)
  const [retryError, setRetryError] = useState(null)
  const [retrying, setRetrying] = useState(false)
  const refreshInterval = useRef(null)

  // Fetch runs from API
  const fetchRuns = useCallback(async () => {
    try {
      // Fetch in-memory pipeline runs
      const pipelineResponse = await pipelineApi.getRuns()
      const newRuns = pipelineResponse.runs || []

      // Only update if changed (prevent re-renders)
      if (JSON.stringify(runs) !== JSON.stringify(newRuns)) {
        setRuns(newRuns)
      }

      // Update selected run if it changed
      if (selectedRun) {
        const updated = newRuns.find(r => r.pipeline_run_id === selectedRun.pipeline_run_id)
        if (updated && JSON.stringify(selectedRun) !== JSON.stringify(updated)) {
          setSelectedRun({ ...updated })
        }
      }
    } catch (error) {
      console.error('Failed to fetch runs:', error)
    } finally {
      setLoadingRuns(false)
    }
  }, [runs, selectedRun, setRuns, setSelectedRun, setLoadingRuns])

  // Auto-refresh every 5 seconds
  useEffect(() => {
    fetchRuns()
    refreshInterval.current = setInterval(fetchRuns, 5000)

    return () => {
      if (refreshInterval.current) {
        clearInterval(refreshInterval.current)
      }
    }
  }, [fetchRuns])

  const showNewRunForm = () => {
    setCreatingNewRun(true)
    setSelectedRun(null)
  }

  const startPipeline = async (config) => {
    setSubmittingPipeline(true)
    setPipelineError(null)

    try {
      const response = await pipelineApi.startPipeline(config)

      const newRun = {
        pipeline_run_id: response.pipeline_run_id,
        experiment_name: config.experiment_name,
        status: response.review_status === 'awaiting_review' ? 'awaiting_review' : 'running',
        created_at: new Date().toISOString(),
        user_prompt: config.user_prompt,
        data_path: config.data_path,
        current_node: 'review_config',
        extracted_config: response.extracted_config,
        confidence: response.confidence,
        reasoning: response.reasoning,
        assumptions: response.assumptions,
        config_warnings: response.config_warnings,
        bedrock_model_id: response.bedrock_model_id,
        bedrock_tokens_used: response.bedrock_tokens_used,
        data_profile: response.data_profile,
        mlflow_run_id: response.mlflow_run_id,
        mlflow_experiment_id: response.mlflow_experiment_id,
        review_status: response.review_status,
        review_questions: response.review_questions,
        review_summary: response.review_summary,
        review_recommendation: response.review_recommendation,
        completed_nodes: [],
        failed_nodes: []
      }

      setRuns([newRun, ...runs])
      setSelectedRun(newRun)
      setCreatingNewRun(false)
    } catch (error) {
      setPipelineError(error.message || 'Failed to start pipeline')
      console.error('Error starting pipeline:', error)
    } finally {
      setSubmittingPipeline(false)
    }
  }

  const selectRun = (run) => {
    setSelectedRun(run)
    setCreatingNewRun(false)
  }

  const deleteRun = async (runId) => {
    if (!window.confirm('Are you sure you want to delete this run?')) {
      return
    }

    try {
      await pipelineApi.deletePipeline(runId)
      setRuns(runs.filter(r => r.pipeline_run_id !== runId))
      if (selectedRun?.pipeline_run_id === runId) {
        setSelectedRun(null)
      }
    } catch (error) {
      console.error('Failed to delete run:', error)
      alert('Failed to delete run: ' + error.message)
    }
  }

  const stopRun = async (runId) => {
    if (!window.confirm('Are you sure you want to stop this run?')) {
      return
    }

    try {
      await pipelineApi.stopPipeline(runId)
      const updatedRuns = runs.map(r =>
        r.pipeline_run_id === runId ? { ...r, status: 'stopped' } : r
      )
      setRuns(updatedRuns)
    } catch (error) {
      console.error('Failed to stop run:', error)
      alert('Failed to stop run: ' + error.message)
    }
  }

  const handleAlgorithmSelected = (approved) => {
    // Refresh runs to get updated status
    fetchRuns()

    if (approved) {
      alert('✓ Algorithm selected! Agent 1B will now generate preprocessing questions.')
    } else {
      // Show retry/cancel dialog for rejection
      setShowRetryDialog(true)
      setRetryError("Algorithm selection rejected. You can retry analysis with Agent 0 or cancel the pipeline.")
    }
  }

  const handleReviewSubmitted = (approved) => {
    // Refresh runs to get updated status
    fetchRuns()

    if (approved) {
      alert('✓ Review approved! Pipeline will continue.')
    } else {
      // Show retry/cancel dialog for rejection
      setShowRetryDialog(true)
      setRetryError("Configuration rejected. You can retry analysis with Agent 0 or cancel the pipeline.")
    }
  }

  const handlePreprocessingReviewSubmitted = (approved) => {
    // Refresh runs to get updated status
    fetchRuns()

    if (approved) {
      alert('✓ Preprocessing approved! Pipeline will continue to feature engineering.')
    } else {
      alert('🔄 Preprocessing rejected. The pipeline will retry preprocessing with new LLM parameter selection.')
    }
  }

  const handleRetryAgent0 = async () => {
    if (!selectedRun) return

    setRetrying(true)
    setRetryError(null)

    try {
      const response = await pipelineApi.retryAgent0(selectedRun.pipeline_run_id)

      if (response.success) {
        // Success - new review questions generated
        setShowRetryDialog(false)
        fetchRuns()
        alert('✓ Configuration re-analyzed successfully! Please review the updated configuration.')
      } else {
        // Failed - show error but keep dialog open
        setRetryError(response.error || response.message)
      }
    } catch (error) {
      console.error('Failed to retry Agent 0:', error)
      setRetryError(error.response?.data?.detail?.message || error.message || 'Failed to retry Agent 0')
    } finally {
      setRetrying(false)
    }
  }

  const handleCancelPipeline = async () => {
    if (!selectedRun) return

    if (!window.confirm('Are you sure you want to cancel this pipeline?')) {
      return
    }

    try {
      await pipelineApi.cancelAfterRejection(selectedRun.pipeline_run_id)
      setShowRetryDialog(false)
      setRetryError(null)
      fetchRuns()
      alert('Pipeline cancelled successfully.')
    } catch (error) {
      console.error('Failed to cancel pipeline:', error)
      alert('Failed to cancel pipeline: ' + (error.response?.data?.detail?.message || error.message))
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 text-white p-4 overflow-y-auto">
        <button
          onClick={showNewRunForm}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded mb-4"
        >
          + New Run
        </button>

        {/* Active Runs */}
        {runs.length > 0 && (
          <div className="mb-4">
            <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Active Runs</h3>
            <div className="space-y-2">
              {runs.map((run) => (
                <div
                  key={run.pipeline_run_id}
                  onClick={() => selectRun(run)}
                  className={`p-3 rounded cursor-pointer hover:bg-gray-800 ${
                    selectedRun?.pipeline_run_id === run.pipeline_run_id ? 'bg-gray-800 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className="text-sm font-semibold truncate">{run.experiment_name || 'Unnamed'}</div>
                  <div className="text-xs text-gray-400 font-mono truncate">{run.pipeline_run_id.substring(0, 12)}...</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      run.status === 'running' ? 'bg-blue-600' :
                      run.status === 'awaiting_review' ? 'bg-yellow-600' :
                      run.status === 'awaiting_algorithm_selection' ? 'bg-purple-600' :
                      run.status === 'review_rejected_reworking' ? 'bg-orange-600' :
                      run.status === 'review_rejected_awaiting_decision' ? 'bg-purple-600' :
                      run.status === 'review_approved' ? 'bg-green-600' :
                      run.status === 'review_rejected' ? 'bg-red-600' :
                      run.status === 'cancelled_by_user' ? 'bg-gray-600' :
                      run.status === 'preprocessing_completed' ? 'bg-cyan-600' :
                      run.status === 'preprocessing_failed' ? 'bg-red-600' :
                      run.status === 'awaiting_preprocessing_review' ? 'bg-teal-600' :
                      run.status === 'preprocessing_approved' ? 'bg-green-600' :
                      run.status === 'preprocessing_rejected' ? 'bg-orange-600' :
                      run.status === 'completed' ? 'bg-green-600' :
                      run.status === 'failed' ? 'bg-red-600' : 'bg-gray-600'
                    }`}>
                      {run.status === 'awaiting_algorithm_selection' ? 'select algorithm' :
                       run.status === 'review_rejected_reworking' ? 'reworking' :
                       run.status === 'review_rejected_awaiting_decision' ? 'awaiting decision' :
                       run.status === 'cancelled_by_user' ? 'cancelled' :
                       run.status === 'preprocessing_completed' ? 'preprocessing done' :
                       run.status === 'preprocessing_failed' ? 'preprocessing failed' :
                       run.status === 'awaiting_preprocessing_review' ? 'review preprocessing' :
                       run.status === 'preprocessing_approved' ? 'preprocessing approved' :
                       run.status === 'preprocessing_rejected' ? 'preprocessing rejected' :
                       run.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
        {creatingNewRun ? (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">Create New Pipeline Run</h2>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              startPipeline({
                user_prompt: formData.get('user_prompt'),
                data_path: formData.get('data_path'),
                experiment_name: formData.get('experiment_name')
              })
            }}>
              <div className="space-y-4 bg-white p-6 rounded-lg shadow">
                <div>
                  <label className="block text-sm font-medium mb-2">Natural Language Prompt</label>
                  <textarea
                    name="user_prompt"
                    rows="4"
                    className="w-full p-3 border rounded"
                    placeholder="Describe your ML task (e.g., 'Classify iris flowers')"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Data Path</label>
                  <input
                    name="data_path"
                    type="text"
                    className="w-full p-3 border rounded"
                    placeholder="data/iris.csv"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Experiment Name</label>
                  <input
                    name="experiment_name"
                    type="text"
                    className="w-full p-3 border rounded"
                    placeholder="My ML Experiment"
                    required
                  />
                </div>
                {pipelineError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
                    {pipelineError}
                  </div>
                )}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={submittingPipeline}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded disabled:opacity-50"
                  >
                    {submittingPipeline ? 'Starting...' : '🚀 Start Pipeline'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setCreatingNewRun(false)}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-6 rounded"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          </div>
        ) : selectedRun ? (
          <div className="flex gap-6 h-full">
            {/* Left Side - Run Details */}
            <div className="flex-1 overflow-y-auto">
              <h2 className="text-2xl font-bold mb-4">{selectedRun.experiment_name || 'Pipeline Run'}</h2>
              <p className="text-sm text-gray-600 mb-6">Run ID: {selectedRun.pipeline_run_id}</p>

              {selectedRun.extracted_config && (
                <div className="bg-white p-6 rounded-lg shadow mb-6 border-2 border-blue-200">
                  <h3 className="text-xl font-bold mb-2 flex items-center gap-2">
                    <span className="text-2xl">🤖</span> Bedrock AI Analysis
                  </h3>
                  <div className="mb-4">
                    <div className="text-sm font-semibold mb-1">Confidence</div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${
                            selectedRun.confidence >= 0.8 ? 'bg-green-500' :
                            selectedRun.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${selectedRun.confidence * 100}%` }}
                        />
                      </div>
                      <span className="font-bold">{(selectedRun.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <pre className="text-sm overflow-x-auto">{JSON.stringify(selectedRun.extracted_config, null, 2)}</pre>
                  </div>
                </div>
              )}

              {/* Algorithm Selection Form - shown when Agent 1A has recommended algorithms */}
              {selectedRun.pipeline_status === 'awaiting_algorithm_selection' && selectedRun.recommended_algorithms && (
                <AlgorithmSelectionForm
                  run={selectedRun}
                  onAlgorithmSelected={handleAlgorithmSelected}
                />
              )}

              {/* Review Form - shown when review questions are available */}
              {selectedRun.review_questions && selectedRun.review_questions.length > 0 && selectedRun.review_status === 'awaiting_review' && (
                <ReviewForm
                  run={selectedRun}
                  onReviewSubmitted={handleReviewSubmitted}
                />
              )}

              {/* Preprocessing Review Form - shown when preprocessing is complete and awaiting review */}
              {selectedRun.pipeline_status === 'awaiting_preprocessing_review' && selectedRun.preprocessing_summary && (
                <PreprocessingReviewForm
                  run={selectedRun}
                  onReviewSubmitted={handlePreprocessingReviewSubmitted}
                />
              )}

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Pipeline Status</h3>
                <div className="space-y-2">
                  <div>Current Node: <span className="font-mono">{selectedRun.current_node || 'N/A'}</span></div>
                  <div>Completed: {selectedRun.completed_nodes?.length || 0}</div>
                  <div>Failed: {selectedRun.failed_nodes?.length || 0}</div>
                  <div className="mt-4">
                    <span className={`px-3 py-1 rounded text-sm font-semibold ${
                      selectedRun.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      selectedRun.status === 'awaiting_review' ? 'bg-yellow-100 text-yellow-800' :
                      selectedRun.status === 'awaiting_algorithm_selection' ? 'bg-purple-100 text-purple-800' :
                      selectedRun.status === 'review_rejected_reworking' ? 'bg-orange-100 text-orange-800' :
                      selectedRun.status === 'review_rejected_awaiting_decision' ? 'bg-purple-100 text-purple-800' :
                      selectedRun.status === 'review_approved' ? 'bg-green-100 text-green-800' :
                      selectedRun.status === 'review_rejected' ? 'bg-red-100 text-red-800' :
                      selectedRun.status === 'cancelled_by_user' ? 'bg-gray-100 text-gray-800' :
                      selectedRun.status === 'preprocessing_completed' ? 'bg-cyan-100 text-cyan-800' :
                      selectedRun.status === 'preprocessing_failed' ? 'bg-red-100 text-red-800' :
                      selectedRun.status === 'awaiting_preprocessing_review' ? 'bg-teal-100 text-teal-800' :
                      selectedRun.status === 'preprocessing_approved' ? 'bg-green-100 text-green-800' :
                      selectedRun.status === 'preprocessing_rejected' ? 'bg-orange-100 text-orange-800' :
                      selectedRun.status === 'completed' ? 'bg-green-100 text-green-800' :
                      selectedRun.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {selectedRun.status === 'awaiting_algorithm_selection' ? 'AWAITING ALGORITHM SELECTION' :
                       selectedRun.status === 'review_rejected_reworking' ? 'RE-ANALYZING WITH FEEDBACK' :
                       selectedRun.status === 'review_rejected_awaiting_decision' ? 'AWAITING USER DECISION' :
                       selectedRun.status === 'cancelled_by_user' ? 'CANCELLED' :
                       selectedRun.status === 'preprocessing_completed' ? 'PREPROCESSING COMPLETED' :
                       selectedRun.status === 'preprocessing_failed' ? 'PREPROCESSING FAILED' :
                       selectedRun.status === 'awaiting_preprocessing_review' ? 'AWAITING PREPROCESSING REVIEW' :
                       selectedRun.status === 'preprocessing_approved' ? 'PREPROCESSING APPROVED' :
                       selectedRun.status === 'preprocessing_rejected' ? 'PREPROCESSING REJECTED - RETRYING' :
                       selectedRun.status?.toUpperCase().replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Side - LangGraph Visualization */}
            <div className="w-96 overflow-y-auto">
              <LangGraphDiagram
                currentNode={selectedRun.current_node}
                completedNodes={selectedRun.completed_nodes || []}
                failedNodes={selectedRun.failed_nodes || []}
              />
            </div>
          </div>
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">🤖</div>
              <h2 className="text-3xl font-bold mb-4">Welcome to ML Pipeline</h2>
              <p className="text-lg text-gray-600 mb-8">Create a new pipeline run to get started</p>
              <button
                onClick={showNewRunForm}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg text-lg"
              >
                + Create New Run
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Retry/Cancel Dialog */}
      {showRetryDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
            <h3 className="text-xl font-bold mb-4 text-red-600">Configuration Rejected</h3>

            {retryError && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
                <p className="text-sm text-red-800">{retryError}</p>
              </div>
            )}

            <p className="text-gray-700 mb-6">
              The configuration analysis failed or was rejected. You can:
            </p>

            <div className="space-y-3 mb-6">
              <div className="flex items-start">
                <span className="text-blue-600 font-bold mr-2">•</span>
                <div>
                  <strong>Retry with Agent 0:</strong> Re-analyze the configuration with your feedback
                </div>
              </div>
              <div className="flex items-start">
                <span className="text-red-600 font-bold mr-2">•</span>
                <div>
                  <strong>Cancel Pipeline:</strong> Stop this pipeline run
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleRetryAgent0}
                disabled={retrying}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {retrying ? 'Retrying...' : '🔄 Retry with Agent 0'}
              </button>
              <button
                onClick={handleCancelPipeline}
                disabled={retrying}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ❌ Cancel Pipeline
              </button>
            </div>

            <button
              onClick={() => setShowRetryDialog(false)}
              disabled={retrying}
              className="mt-3 w-full text-gray-600 hover:text-gray-800 text-sm disabled:opacity-50"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Home
