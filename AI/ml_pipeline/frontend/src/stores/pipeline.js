import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePipelineStore = defineStore('pipeline', () => {
  // State
  const activePipeline = ref(null)
  const currentState = ref({})
  const isConnected = ref(false)
  const error = ref(null)

  // Getters
  const isRunning = computed(() => {
    return activePipeline.value?.status === 'running'
  })

  const currentNode = computed(() => {
    return currentState.value?.current_node || null
  })

  const progress = computed(() => {
    const completed = currentState.value?.completed_nodes || []
    const total = currentState.value?.total_nodes || 0
    return total > 0 ? Math.round((completed.length / total) * 100) : 0
  })

  const errors = computed(() => {
    return currentState.value?.errors || []
  })

  // Actions
  function startPipeline(pipelineData) {
    activePipeline.value = {
      runId: pipelineData.pipeline_run_id,
      experimentId: pipelineData.mlflow_experiment_id,
      status: 'running',
      startedAt: new Date().toISOString()
    }
    currentState.value = pipelineData
    error.value = null
  }

  function updateState(state) {
    currentState.value = { ...currentState.value, ...state }

    // Update active pipeline status if changed
    if (state.status && activePipeline.value) {
      activePipeline.value.status = state.status
    }
  }

  function stopPipeline() {
    if (activePipeline.value) {
      activePipeline.value.status = 'stopped'
    }
  }

  function completePipeline() {
    if (activePipeline.value) {
      activePipeline.value.status = 'completed'
      activePipeline.value.completedAt = new Date().toISOString()
    }
  }

  function failPipeline(errorMessage) {
    if (activePipeline.value) {
      activePipeline.value.status = 'failed'
    }
    error.value = errorMessage
  }

  function reset() {
    activePipeline.value = null
    currentState.value = {}
    isConnected.value = false
    error.value = null
  }

  function setConnected(connected) {
    isConnected.value = connected
  }

  return {
    // State
    activePipeline,
    currentState,
    isConnected,
    error,

    // Getters
    isRunning,
    currentNode,
    progress,
    errors,

    // Actions
    startPipeline,
    updateState,
    stopPipeline,
    completePipeline,
    failPipeline,
    reset,
    setConnected
  }
})
