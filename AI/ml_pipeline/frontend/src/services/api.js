import axios from 'axios'
import { API_BASE_URL } from '../utils/constants'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for long-running operations
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Add any auth tokens here if needed
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response.data,
  error => {
    // Handle errors globally
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
    console.error('API Error:', errorMessage)
    return Promise.reject(new Error(errorMessage))
  }
)

// Pipeline API endpoints
export const pipelineApi = {
  /**
   * Start a new pipeline with natural language prompt
   * @param {Object} config - Pipeline configuration
   * @returns {Promise}
   */
  startPipeline(config) {
    return api.post('/api/pipeline/load-data', config)
  },

  /**
   * Get pipeline state by run ID
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  getPipelineState(runId) {
    return api.get(`/api/pipeline/state/${runId}`)
  },

  /**
   * Stop a running pipeline
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  stopPipeline(runId) {
    return api.post(`/api/pipeline/stop/${runId}`)
  },

  /**
   * Delete a pipeline
   * @param {string} runId - Pipeline run ID
   * @param {boolean} deleteExperiment - Also delete MLflow experiment
   * @returns {Promise}
   */
  deletePipeline(runId, deleteExperiment = false) {
    return api.delete(`/api/pipeline/delete/${runId}`, {
      params: { delete_experiment: deleteExperiment }
    })
  },

  /**
   * Get list of all pipeline runs
   * @param {Object} filters - Optional filters (status, experiment, etc.)
   * @returns {Promise}
   */
  getRuns(filters = {}) {
    return api.get('/api/pipeline/runs', { params: filters })
  },

  /**
   * Submit algorithm selection (after Agent 1A recommends algorithms)
   * @param {string} runId - Pipeline run ID
   * @param {Object} selectionData - { selected_algorithm: string, approved: boolean, user_feedback: string }
   * @returns {Promise}
   */
  submitAlgorithmSelection(runId, selectionData) {
    return api.post(`/api/pipeline/algorithm-selection/${runId}/submit`, selectionData)
  },

  /**
   * Continue pipeline after algorithm selection is approved
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  continueAfterAlgorithmSelection(runId) {
    return api.post(`/api/pipeline/algorithm-selection/${runId}/continue`)
  },

  /**
   * Submit review answers for a pipeline run
   * @param {string} runId - Pipeline run ID
   * @param {Object} reviewData - Review answers and approval status
   * @returns {Promise}
   */
  submitReviewAnswers(runId, reviewData) {
    return api.post(`/api/pipeline/review/${runId}/submit`, reviewData)
  },

  /**
   * Continue pipeline execution after review approval
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  continuePipeline(runId) {
    return api.post(`/api/pipeline/${runId}/continue`)
  },

  /**
   * Retry Agent 0 configuration extraction after rejection
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  retryAgent0(runId) {
    return api.post(`/api/pipeline/${runId}/retry-agent0`)
  },

  /**
   * Cancel pipeline after review rejection
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  cancelAfterRejection(runId) {
    return api.post(`/api/pipeline/${runId}/cancel-after-rejection`)
  },

  /**
   * Submit preprocessing review (approve/reject preprocessing results)
   * @param {string} runId - Pipeline run ID
   * @param {Object} reviewData - { approved: boolean, user_feedback: string }
   * @returns {Promise}
   */
  submitPreprocessingReview(runId, reviewData) {
    return api.post(`/api/pipeline/preprocessing-review/${runId}/submit`, reviewData)
  },

  /**
   * Get LangGraph visualization image
   * @returns {string} URL to the graph visualization image
   */
  getGraphVisualization() {
    return `${API_BASE_URL}/api/pipeline/graph-visualization`
  }
}

// Health check
export const healthApi = {
  /**
   * Check if backend is healthy
   * @returns {Promise}
   */
  check() {
    return api.get('/health')
  }
}

export default api
