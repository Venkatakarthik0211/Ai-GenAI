<template>
  <div class="card">
    <h3 class="text-lg font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
      📋 Pipeline Execution Log
    </h3>

    <div class="space-y-3">
      <!-- Node Timeline -->
      <div
        v-for="(node, index) in nodeTimeline"
        :key="index"
        class="relative pl-8 pb-4 border-l-2"
        :class="{
          'border-green-500': node.status === 'completed',
          'border-blue-500': node.status === 'in-progress',
          'border-red-500': node.status === 'failed',
          'border-gray-300': node.status === 'pending'
        }"
      >
        <!-- Node Status Icon -->
        <div
          class="absolute -left-3 top-0 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs"
          :class="{
            'bg-green-500': node.status === 'completed',
            'bg-blue-500 animate-pulse': node.status === 'in-progress',
            'bg-red-500': node.status === 'failed',
            'bg-gray-300': node.status === 'pending'
          }"
        >
          <span v-if="node.status === 'completed'">✓</span>
          <span v-else-if="node.status === 'in-progress'">•••</span>
          <span v-else-if="node.status === 'failed'">✕</span>
          <span v-else>○</span>
        </div>

        <!-- Node Content -->
        <div class="bg-white dark:bg-dark-card-bg rounded-lg p-4 shadow-sm">
          <!-- Node Header -->
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-medium text-sm text-gray-900 dark:text-gray-100">
              {{ formatNodeName(node.name) }}
            </h4>
            <span
              class="text-xs px-2 py-1 rounded"
              :class="{
                'bg-green-100 text-green-800': node.status === 'completed',
                'bg-blue-100 text-blue-800': node.status === 'in-progress',
                'bg-red-100 text-red-800': node.status === 'failed',
                'bg-gray-100 text-gray-600': node.status === 'pending'
              }"
            >
              {{ node.status }}
            </span>
          </div>

          <!-- Node Output -->
          <div v-if="node.output" class="mt-3 text-sm text-gray-900 dark:text-gray-100">
            <!-- Bedrock Config Extraction -->
            <div v-if="node.name === 'analyze_prompt' && node.output.extracted_config">
              <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded mb-2">
                <div class="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                  🤖 Bedrock Config Extraction
                </div>
                <div class="space-y-2">
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-gray-600 dark:text-gray-300">Confidence:</span>
                    <span
                      class="font-bold"
                      :class="{
                        'text-green-600': node.output.confidence >= 0.8,
                        'text-yellow-600': node.output.confidence >= 0.6 && node.output.confidence < 0.8,
                        'text-red-600': node.output.confidence < 0.6
                      }"
                    >
                      {{ (node.output.confidence * 100).toFixed(0) }}%
                    </span>
                  </div>

                  <div class="bg-white dark:bg-gray-800 p-2 rounded text-xs">
                    <div class="font-medium mb-1 text-gray-700 dark:text-gray-300">Extracted Config:</div>
                    <pre class="text-xs overflow-x-auto text-gray-900 dark:text-gray-100">{{ JSON.stringify(node.output.extracted_config, null, 2) }}</pre>
                  </div>

                  <div v-if="node.output.reasoning" class="bg-white dark:bg-gray-800 p-2 rounded text-xs">
                    <div class="font-medium mb-1 text-gray-700 dark:text-gray-300">Reasoning:</div>
                    <div class="whitespace-pre-wrap text-gray-900 dark:text-gray-100">{{ node.output.reasoning }}</div>
                  </div>

                  <div v-if="node.output.bedrock_model_id" class="text-xs text-gray-600 dark:text-gray-400">
                    Model: {{ node.output.bedrock_model_id }}
                    <span v-if="node.output.bedrock_tokens_used">
                      | Tokens: {{ node.output.bedrock_tokens_used }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Data Loading -->
            <div v-else-if="node.name === 'load_data' && node.output.data_profile">
              <div class="bg-purple-50 dark:bg-purple-900/20 p-3 rounded">
                <div class="font-semibold text-purple-900 dark:text-purple-100 mb-2">
                  📊 Data Loaded
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span class="text-gray-600 dark:text-gray-300">Samples:</span>
                    <span class="ml-2 font-bold text-gray-900 dark:text-gray-100">{{ node.output.data_profile.n_samples }}</span>
                  </div>
                  <div>
                    <span class="text-gray-600 dark:text-gray-300">Features:</span>
                    <span class="ml-2 font-bold text-gray-900 dark:text-gray-100">{{ node.output.data_profile.n_features }}</span>
                  </div>
                  <div v-if="node.output.data_profile.target_distribution" class="col-span-2">
                    <span class="text-gray-600 dark:text-gray-300">Target Distribution:</span>
                    <div class="mt-1 bg-white dark:bg-gray-800 p-2 rounded">
                      <pre class="text-xs text-gray-900 dark:text-gray-100">{{ JSON.stringify(node.output.data_profile.target_distribution, null, 2) }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Algorithm Selection -->
            <div v-else-if="node.name === 'select_algorithms' && node.output.selected_algorithms">
              <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded">
                <div class="font-semibold text-green-900 dark:text-green-100 mb-2">
                  🎯 Algorithms Selected
                </div>
                <div class="flex flex-wrap gap-2 mb-2">
                  <span
                    v-for="algo in node.output.selected_algorithms"
                    :key="algo"
                    class="px-2 py-1 bg-green-200 dark:bg-green-800 text-green-900 dark:text-green-100 rounded text-xs font-medium"
                  >
                    {{ algo }}
                  </span>
                </div>
                <div v-if="node.output.reasoning" class="text-xs bg-white dark:bg-gray-800 p-2 rounded text-gray-900 dark:text-gray-100">
                  {{ node.output.reasoning }}
                </div>
              </div>
            </div>

            <!-- Generic Output -->
            <div v-else-if="node.output.summary" class="bg-gray-50 dark:bg-gray-800 p-3 rounded text-xs text-gray-900 dark:text-gray-100">
              {{ node.output.summary }}
            </div>
          </div>

          <!-- Duration -->
          <div v-if="node.duration" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
            ⏱️ {{ node.duration }}
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="nodeTimeline.length === 0" class="text-center py-8 text-gray-400">
        No execution log available yet
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  completedNodes: {
    type: Array,
    default: () => []
  },
  currentNode: {
    type: String,
    default: null
  },
  failedNodes: {
    type: Array,
    default: () => []
  },
  extractedConfig: {
    type: Object,
    default: null
  },
  confidence: {
    type: Number,
    default: null
  },
  reasoning: {
    type: String,
    default: null
  },
  bedrockModelId: {
    type: String,
    default: null
  },
  bedrockTokensUsed: {
    type: Number,
    default: null
  },
  dataProfile: {
    type: Object,
    default: null
  }
})

// All possible nodes in the pipeline
const allNodes = [
  'analyze_prompt',
  'load_data',
  'clean_data',
  'handle_missing',
  'encode_categorical',
  'scale_features',
  'split_data',
  'select_algorithms',
  'train_models',
  'select_best_model',
  'evaluate_model'
]

const nodeTimeline = computed(() => {
  return allNodes.map(nodeName => {
    let status = 'pending'
    let output = null

    if (props.failedNodes.includes(nodeName)) {
      status = 'failed'
    } else if (props.completedNodes.includes(nodeName)) {
      status = 'completed'

      // Add output data based on node
      if (nodeName === 'analyze_prompt' && props.extractedConfig) {
        output = {
          extracted_config: props.extractedConfig,
          confidence: props.confidence,
          reasoning: props.reasoning,
          bedrock_model_id: props.bedrockModelId,
          bedrock_tokens_used: props.bedrockTokensUsed
        }
      } else if (nodeName === 'load_data' && props.dataProfile) {
        output = {
          data_profile: props.dataProfile
        }
      }
    } else if (nodeName === props.currentNode) {
      status = 'in-progress'
    }

    return {
      name: nodeName,
      status,
      output
    }
  })
})

function formatNodeName(nodeName) {
  return nodeName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
