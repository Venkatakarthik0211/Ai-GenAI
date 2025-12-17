<template>
  <div v-if="config" class="card border-2 border-blue-200 dark:border-blue-800 shadow-lg">
    <!-- Header with Bedrock Branding -->
    <div class="mb-4 flex items-center justify-between border-b border-blue-200 pb-3 dark:border-blue-800">
      <h3 class="text-xl font-bold flex items-center gap-2">
        <span class="text-2xl">🤖</span>
        <span>Bedrock AI Analysis</span>
      </h3>
      <div v-if="bedrockModelId" class="text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
        {{ bedrockModelId.split(':')[0].split('.').pop() }}
      </div>
    </div>

    <!-- Confidence Score - More Prominent -->
    <div v-if="confidence" class="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 p-4 rounded-lg">
      <div class="mb-3 flex items-center justify-between">
        <span class="text-base font-semibold">Extraction Confidence</span>
        <span class="text-2xl font-bold" :class="confidenceColor">
          {{ (confidence * 100).toFixed(0) }}%
        </span>
      </div>
      <div class="h-3 w-full rounded-full bg-gray-200 dark:bg-gray-700 shadow-inner">
        <div
          class="h-3 rounded-full transition-all duration-500 shadow-sm"
          :class="confidenceBarColor"
          :style="{ width: `${confidence * 100}%` }"
        ></div>
      </div>
    </div>

    <!-- Extracted Configuration -->
    <div class="mb-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
      <div class="grid gap-3">
        <div v-for="(value, key) in config" :key="key" class="flex justify-between">
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
            {{ formatKey(key) }}:
          </span>
          <span class="text-sm font-semibold">
            {{ formatValue(value) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Reasoning -->
    <div v-if="reasoning" class="mb-4">
      <h4 class="mb-2 text-sm font-semibold">Reasoning</h4>
      <div class="rounded-lg bg-blue-50 p-3 text-sm dark:bg-blue-900">
        <div v-if="typeof reasoning === 'string'" class="whitespace-pre-wrap">
          {{ reasoning }}
        </div>
        <ul v-else class="list-disc space-y-1 pl-5">
          <li v-for="(value, key) in reasoning" :key="key">
            <strong>{{ formatKey(key) }}:</strong> {{ value }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Assumptions -->
    <div v-if="assumptions && assumptions.length > 0" class="mb-4">
      <h4 class="mb-2 text-sm font-semibold">Assumptions</h4>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(assumption, index) in assumptions"
          :key="index"
          class="badge badge-info"
        >
          {{ assumption }}
        </span>
      </div>
    </div>

    <!-- Warnings -->
    <div v-if="warnings && warnings.length > 0">
      <h4 class="mb-2 text-sm font-semibold">Warnings</h4>
      <div class="space-y-2">
        <div
          v-for="(warning, index) in warnings"
          :key="index"
          class="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
        >
          ⚠️ {{ warning }}
        </div>
      </div>
    </div>

    <!-- Bedrock Model Info -->
    <div v-if="bedrockModelId" class="mt-4 border-t border-gray-200 pt-4 dark:border-dark-border">
      <div class="flex items-center justify-between text-xs text-gray-500">
        <span>Model: {{ bedrockModelId }}</span>
        <span v-if="tokensUsed">Tokens: {{ tokensUsed }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  config: {
    type: Object,
    default: null
  },
  confidence: {
    type: Number,
    default: null
  },
  reasoning: {
    type: [String, Object],
    default: null
  },
  assumptions: {
    type: Array,
    default: () => []
  },
  warnings: {
    type: Array,
    default: () => []
  },
  bedrockModelId: {
    type: String,
    default: null
  },
  tokensUsed: {
    type: Number,
    default: null
  }
})

const confidenceColor = computed(() => {
  if (props.confidence >= 0.8) return 'text-green-600'
  if (props.confidence >= 0.6) return 'text-yellow-600'
  return 'text-red-600'
})

const confidenceBarColor = computed(() => {
  if (props.confidence >= 0.8) return 'bg-green-500'
  if (props.confidence >= 0.6) return 'bg-yellow-500'
  return 'bg-red-500'
})

function formatKey(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

function formatValue(value) {
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
</script>
