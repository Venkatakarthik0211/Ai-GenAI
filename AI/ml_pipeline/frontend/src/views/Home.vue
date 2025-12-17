<template>
  <div class="flex h-screen w-screen overflow-hidden">
    <!-- Sidebar -->
    <Sidebar
      :runs="runs"
      :selected-run-id="selectedRun?.pipeline_run_id"
      :loading="loadingRuns"
      @new-run="showNewRunForm"
      @select-run="selectRun"
      @delete-run="deleteRun"
      @stop-run="stopRun"
    />

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto bg-gray-50 dark:bg-dark-bg">
      <div class="container mx-auto p-6">
        <!-- New Run Form -->
        <div v-if="creatingNewRun" class="flex items-start justify-center">
          <PromptInput
            ref="promptInputRef"
            :loading="submittingPipeline"
            :error="pipelineError"
            :on-cancel="() => creatingNewRun = false"
            @submit="startPipeline"
          />
        </div>

        <!-- Active/Selected Run View -->
        <div v-else-if="selectedRun" class="space-y-6">
          <!-- Header -->
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold">
                {{ selectedRun.experiment_name || 'Pipeline Run' }}
              </h2>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Run ID: {{ selectedRun.pipeline_run_id }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span
                class="badge"
                :class="{
                  'badge-info': selectedRun.status === 'running',
                  'badge-success': selectedRun.status === 'completed',
                  'badge-error': selectedRun.status === 'failed'
                }"
              >
                {{ selectedRun.status }}
              </span>
            </div>
          </div>

          <!-- Pipeline Configuration (if natural language) - PROMINENT -->
          <PipelineConfig
            v-if="selectedRun.extracted_config"
            :config="selectedRun.extracted_config"
            :confidence="selectedRun.confidence"
            :reasoning="selectedRun.reasoning"
            :assumptions="selectedRun.assumptions"
            :warnings="selectedRun.config_warnings"
            :bedrock-model-id="selectedRun.bedrock_model_id"
            :tokens-used="selectedRun.bedrock_tokens_used"
          />

          <!-- Two Column Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column: State Diagram -->
            <div>
              <StateChart
                :current-node="selectedRun.current_node"
                :completed-nodes="selectedRun.completed_nodes || []"
                :failed-nodes="selectedRun.failed_nodes || []"
                :mode="selectedRun.user_prompt ? 'natural_language' : 'traditional'"
              />
            </div>

            <!-- Right Column: Execution Log -->
            <div>
              <NodeExecutionLog
                :completed-nodes="selectedRun.completed_nodes || []"
                :current-node="selectedRun.current_node"
                :failed-nodes="selectedRun.failed_nodes || []"
                :extracted-config="selectedRun.extracted_config"
                :confidence="selectedRun.confidence"
                :reasoning="selectedRun.reasoning"
                :bedrock-model-id="selectedRun.bedrock_model_id"
                :bedrock-tokens-used="selectedRun.bedrock_tokens_used"
                :data-profile="selectedRun.data_profile"
              />
            </div>
          </div>

          <!-- Metrics Panel - Full Width -->
          <MetricsPanel
            :data-profile="selectedRun.data_profile"
            :progress="calculateProgress(selectedRun)"
            :current-node="selectedRun.current_node"
            :pipeline-run-id="selectedRun.pipeline_run_id"
            :mlflow-run-id="selectedRun.mlflow_run_id"
            :mlflow-experiment-id="selectedRun.mlflow_experiment_id"
          />
        </div>

        <!-- Welcome State -->
        <div v-else class="flex h-full items-center justify-center">
          <div class="text-center">
            <div class="mb-4 text-6xl">🤖</div>
            <h2 class="mb-4 text-3xl font-bold">Welcome to ML Pipeline</h2>
            <p class="mb-8 text-lg text-gray-600 dark:text-gray-400">
              Create a new pipeline run to get started
            </p>
            <button
              @click="showNewRunForm"
              class="btn btn-primary btn-lg"
            >
              <span class="text-xl mr-2">+</span> Create New Run
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { usePipelineStore } from '../stores/pipeline'
import { useRunsStore } from '../stores/runs'
import { pipelineApi } from '../services/api'
import Sidebar from '../components/layout/Sidebar.vue'
import PromptInput from '../components/pipeline/PromptInput.vue'
import StateChart from '../components/pipeline/StateChart.vue'
import PipelineConfig from '../components/pipeline/PipelineConfig.vue'
import MetricsPanel from '../components/pipeline/MetricsPanel.vue'
import NodeExecutionLog from '../components/pipeline/NodeExecutionLog.vue'

const pipelineStore = usePipelineStore()
const runsStore = useRunsStore()

// State
const creatingNewRun = ref(false)
const submittingPipeline = ref(false)
const pipelineError = ref(null)
const loadingRuns = ref(false)
const selectedRun = ref(null)
const promptInputRef = ref(null)
const refreshInterval = ref(null)

// Computed
const runs = ref([])

// Lifecycle
onMounted(() => {
  fetchRuns()
  // Auto-refresh runs every 5 seconds
  refreshInterval.value = setInterval(fetchRuns, 5000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})

// Methods
async function fetchRuns() {
  try {
    const response = await pipelineApi.getRuns()
    const newRuns = response.runs || []

    // Only update if runs actually changed (prevent unnecessary re-renders)
    const hasChanges = JSON.stringify(runs.value) !== JSON.stringify(newRuns)
    if (hasChanges) {
      runs.value = newRuns
      runsStore.setRuns(newRuns)
    }

    // Update selected run only if its data changed (prevents Mermaid re-render glitch)
    if (selectedRun.value) {
      const updated = newRuns.find(r => r.pipeline_run_id === selectedRun.value.pipeline_run_id)
      if (updated) {
        const hasSelectedRunChanged = JSON.stringify(selectedRun.value) !== JSON.stringify(updated)
        if (hasSelectedRunChanged) {
          selectedRun.value = { ...updated }
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch runs:', error)
  } finally {
    loadingRuns.value = false
  }
}

function showNewRunForm() {
  creatingNewRun.value = true
  selectedRun.value = null
}

async function startPipeline(config) {
  submittingPipeline.value = true
  pipelineError.value = null

  try {
    const response = await pipelineApi.startPipeline(config)

    // Update store
    pipelineStore.startPipeline(response)

    // Add to runs list
    const newRun = {
      pipeline_run_id: response.pipeline_run_id,
      experiment_name: config.experiment_name,
      status: 'running',
      created_at: new Date().toISOString(),
      user_prompt: config.user_prompt,
      data_path: config.data_path,
      current_node: 'analyze_prompt',
      extracted_config: response.extracted_config,
      confidence: response.confidence,
      reasoning: response.reasoning,
      assumptions: response.assumptions,
      config_warnings: response.config_warnings,
      bedrock_model_id: response.bedrock_model_id,
      bedrock_tokens_used: response.bedrock_tokens_used,
      data_profile: response.data_profile,
      mlflow_run_id: response.mlflow_run_id,
      mlflow_experiment_id: response.mlflow_experiment_id
    }

    runs.value.unshift(newRun)
    runsStore.addRun(newRun)

    // Select the new run
    selectedRun.value = newRun
    creatingNewRun.value = false

    // Reset form
    if (promptInputRef.value) {
      promptInputRef.value.reset()
    }

    console.log('Pipeline started successfully:', response)
  } catch (error) {
    pipelineError.value = error.message || 'Failed to start pipeline'
    console.error('Error starting pipeline:', error)
  } finally {
    submittingPipeline.value = false
  }
}

function selectRun(run) {
  selectedRun.value = run
  creatingNewRun.value = false
}

async function deleteRun(runId) {
  if (!confirm('Are you sure you want to delete this run?')) {
    return
  }

  try {
    await pipelineApi.deletePipeline(runId)
    runs.value = runs.value.filter(r => r.pipeline_run_id !== runId)
    runsStore.removeRun(runId)

    if (selectedRun.value?.pipeline_run_id === runId) {
      selectedRun.value = null
    }

    console.log('Run deleted:', runId)
  } catch (error) {
    console.error('Failed to delete run:', error)
    alert('Failed to delete run: ' + error.message)
  }
}

async function stopRun(runId) {
  if (!confirm('Are you sure you want to stop this run?')) {
    return
  }

  try {
    await pipelineApi.stopPipeline(runId)

    // Update run status
    const run = runs.value.find(r => r.pipeline_run_id === runId)
    if (run) {
      run.status = 'stopped'
      runsStore.updateRun(runId, { status: 'stopped' })
    }

    console.log('Run stopped:', runId)
  } catch (error) {
    console.error('Failed to stop run:', error)
    alert('Failed to stop run: ' + error.message)
  }
}

function calculateProgress(run) {
  const completed = run.completed_nodes?.length || 0
  const total = 11 // Total number of nodes in pipeline
  return Math.round((completed / total) * 100)
}
</script>
