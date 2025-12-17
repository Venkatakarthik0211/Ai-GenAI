<template>
  <div class="card">
    <h3 class="mb-4 text-lg font-semibold">Pipeline Metrics</h3>

    <!-- Data Profile -->
    <div v-if="dataProfile" class="mb-6">
      <h4 class="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
        Data Profile
      </h4>
      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
          <div class="text-2xl font-bold text-primary-600">
            {{ dataProfile.n_samples?.toLocaleString() }}
          </div>
          <div class="text-xs text-gray-600 dark:text-gray-400">
            Samples
          </div>
        </div>
        <div class="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
          <div class="text-2xl font-bold text-primary-600">
            {{ dataProfile.n_features }}
          </div>
          <div class="text-xs text-gray-600 dark:text-gray-400">
            Features
          </div>
        </div>
      </div>

      <!-- Target Column -->
      <div v-if="dataProfile.target_column" class="mt-3">
        <div class="text-sm">
          <span class="font-medium text-gray-600 dark:text-gray-400">Target:</span>
          <span class="ml-2 font-semibold">{{ dataProfile.target_column }}</span>
        </div>
      </div>

      <!-- Target Distribution -->
      <div v-if="dataProfile.target_distribution" class="mt-3">
        <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
          Target Distribution:
        </div>
        <div class="space-y-2">
          <div
            v-for="(count, label) in dataProfile.target_distribution"
            :key="label"
            class="flex items-center justify-between"
          >
            <span class="text-xs">{{ label }}</span>
            <div class="flex items-center gap-2 flex-1 ml-3">
              <div class="h-2 flex-1 rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  class="h-2 rounded-full bg-primary-500"
                  :style="{ width: `${(count / dataProfile.n_samples) * 100}%` }"
                ></div>
              </div>
              <span class="text-xs font-medium w-12 text-right">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress -->
    <div v-if="progress !== null" class="mb-6">
      <h4 class="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
        Progress
      </h4>
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm">{{ currentNode || 'Not started' }}</span>
        <span class="text-sm font-bold">{{ progress }}%</span>
      </div>
      <div class="h-3 w-full rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          class="h-3 rounded-full bg-primary-500 transition-all duration-500"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>

    <!-- MLflow Links -->
    <div class="border-t border-gray-200 pt-4 dark:border-dark-border">
      <h4 class="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
        Quick Links
      </h4>
      <div class="space-y-2">
        <a
          v-if="mlflowUrl && mlflowRunId"
          :href="`${mlflowUrl}/#/experiments/${mlflowExperimentId}/runs/${mlflowRunId}`"
          target="_blank"
          class="btn btn-secondary btn-sm w-full"
        >
          🔬 View in MLflow
        </a>
        <button
          v-if="pipelineRunId"
          @click="$emit('view-logs')"
          class="btn btn-secondary btn-sm w-full"
        >
          📋 View Logs
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MLFLOW_URL } from '../../utils/constants'

const props = defineProps({
  dataProfile: {
    type: Object,
    default: null
  },
  progress: {
    type: Number,
    default: null
  },
  currentNode: {
    type: String,
    default: null
  },
  pipelineRunId: {
    type: String,
    default: null
  },
  mlflowRunId: {
    type: String,
    default: null
  },
  mlflowExperimentId: {
    type: String,
    default: null
  }
})

defineEmits(['view-logs'])

const mlflowUrl = computed(() => MLFLOW_URL)
</script>
