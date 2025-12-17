<template>
  <div class="card">
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-lg font-semibold">LangGraph State Diagram</h3>
      <div v-if="currentNode" class="badge badge-info">
        Current: {{ currentNode }}
      </div>
    </div>

    <div
      ref="mermaidContainer"
      class="overflow-auto rounded-lg border border-gray-200 bg-white p-4 dark:border-dark-border dark:bg-dark-surface"
      style="min-height: 400px"
    >
      <div v-if="loading" class="flex items-center justify-center h-96">
        <div class="text-center">
          <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p class="mt-2 text-sm text-gray-500">Loading diagram...</p>
        </div>
      </div>

      <div v-else-if="error" class="flex items-center justify-center h-96">
        <div class="text-center text-red-600">
          <p>{{ error }}</p>
        </div>
      </div>

      <div v-else class="mermaid-diagram" v-html="renderedDiagram"></div>
    </div>

    <!-- Legend -->
    <div class="mt-4 flex flex-wrap gap-4 text-sm">
      <div class="flex items-center gap-2">
        <span class="inline-block h-3 w-3 rounded-full bg-gray-400"></span>
        <span>Pending</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-block h-3 w-3 rounded-full bg-blue-500 animate-pulse"></span>
        <span>In Progress</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-block h-3 w-3 rounded-full bg-green-500"></span>
        <span>Completed</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-block h-3 w-3 rounded-full bg-red-500"></span>
        <span>Failed</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import mermaid from 'mermaid'

const props = defineProps({
  currentNode: {
    type: String,
    default: null
  },
  completedNodes: {
    type: Array,
    default: () => []
  },
  failedNodes: {
    type: Array,
    default: () => []
  },
  mode: {
    type: String,
    default: 'natural_language' // or 'traditional'
  }
})

const mermaidContainer = ref(null)
const renderedDiagram = ref('')
const loading = ref(true)
const error = ref(null)

// Initialize Mermaid
onMounted(() => {
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis'
    }
  })
  renderDiagram()
})

// Watch for prop changes - deep watch to catch array updates
watch([() => props.currentNode, () => props.completedNodes, () => props.failedNodes], () => {
  renderDiagram()
}, { deep: true })

const mermaidCode = computed(() => {
  const completed = props.completedNodes || []
  const failed = props.failedNodes || []
  const current = props.currentNode

  // Build node style definitions
  let styles = ''
  if (current) {
    styles += `    style ${current} fill:#3B82F6,stroke:#1E40AF,stroke-width:4px,color:#fff\n`
  }
  completed.forEach(node => {
    if (node !== current) {
      styles += `    style ${node} fill:#10B981,stroke:#059669,stroke-width:2px,color:#fff\n`
    }
  })
  failed.forEach(node => {
    styles += `    style ${node} fill:#EF4444,stroke:#DC2626,stroke-width:2px,color:#fff\n`
  })

  // Build diagram
  const entryPoint = props.mode === 'natural_language'
    ? `    Start([Start]) --> Conditional{{Input Mode?}}
    Conditional -->|Natural Language| analyze_prompt[Analyze Prompt<br/>Bedrock Extraction]
    Conditional -->|Traditional| load_data[Load Data]
    analyze_prompt --> load_data`
    : `    Start([Start]) --> load_data[Load Data]`

  return `graph TD
${entryPoint}
    load_data --> clean_data[Clean Data]
    clean_data --> handle_missing[Handle Missing]
    handle_missing --> encode_features[Encode Features]
    encode_features --> scale_features[Scale Features]
    scale_features --> split_data[Split Data]
    split_data --> train_models[Train Models]
    train_models --> evaluate_models[Evaluate Models]
    evaluate_models --> select_best[Select Best]
    select_best --> generate_report[Generate Report]
    generate_report --> End([Complete])

${styles}
    classDef default fill:#E5E7EB,stroke:#9CA3AF,stroke-width:2px
    classDef startEnd fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px
    classDef decision fill:#FFF3E0,stroke:#F57C00,stroke-width:2px

    class Start,End startEnd
    class Conditional decision`
})

async function renderDiagram() {
  loading.value = true
  error.value = null

  try {
    const { svg } = await mermaid.render('mermaid-diagram', mermaidCode.value)
    renderedDiagram.value = svg
  } catch (err) {
    console.error('Mermaid rendering error:', err)
    error.value = 'Failed to render diagram'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mermaid-diagram :deep(svg) {
  max-width: 100%;
  height: auto;
}
</style>
