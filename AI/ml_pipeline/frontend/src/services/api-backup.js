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
   * Get detailed information about a specific run
   * @param {string} runId - Pipeline run ID
   * @returns {Promise}
   */
  getRunDetails(runId) {
    return api.get(`/api/pipeline/run/${runId}`)
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
