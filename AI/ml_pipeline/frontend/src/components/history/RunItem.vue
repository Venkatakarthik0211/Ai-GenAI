<template>
  <div
    @click="$emit('click')"
    class="group relative cursor-pointer border-b border-gray-100 px-4 py-3 hover:bg-gray-100 dark:border-dark-border dark:hover:bg-gray-700"
    :class="{ 'bg-primary-50 dark:bg-primary-900': active }"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1 min-w-0">
        <!-- Status and Run ID -->
        <div class="flex items-center gap-2 mb-1">
          <span
            class="status-indicator"
            :class="statusClass"
          ></span>
          <span class="text-xs font-mono text-gray-600 dark:text-dark-text-secondary truncate">
            {{ shortRunId }}
          </span>
        </div>

        <!-- Experiment Name -->
        <div class="text-sm font-medium text-gray-900 dark:text-dark-text truncate mb-1">
          {{ run.experiment_name || 'Unnamed Experiment' }}
        </div>

        <!-- Time -->
        <div class="text-xs text-gray-500 dark:text-dark-text-secondary">
          {{ relativeTime }}
        </div>

        <!-- Current Node (if running) -->
        <div v-if="run.status === 'running' && run.current_node" class="mt-1">
          <span class="text-xs text-blue-600 dark:text-blue-400">
            {{ run.current_node }}
          </span>
        </div>
      </div>

      <!-- Actions (on hover) -->
      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          v-if="run.status === 'running'"
          @click.stop="$emit('stop')"
          class="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900"
          title="Stop"
        >
          <span class="text-red-600">🛑</span>
        </button>
        <button
          @click.stop="$emit('delete')"
          class="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900"
          title="Delete"
        >
          <span class="text-red-600">🗑️</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { STATUS_ICONS, PIPELINE_STATUS } from '../../utils/constants'

const props = defineProps({
  run: {
    type: Object,
    required: true
  },
  active: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click', 'delete', 'stop'])

const shortRunId = computed(() => {
  return props.run.pipeline_run_id?.substring(0, 8) || 'unknown'
})

const statusClass = computed(() => {
  const status = props.run.status
  if (status === PIPELINE_STATUS.RUNNING) return 'status-running'
  if (status === PIPELINE_STATUS.COMPLETED) return 'status-completed'
  if (status === PIPELINE_STATUS.FAILED) return 'status-failed'
  return 'status-pending'
})

const relativeTime = computed(() => {
  const date = new Date(props.run.created_at || props.run.started_at)
  const now = new Date()
  const diff = now - date

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
})
</script>
