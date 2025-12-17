<template>
  <div class="sidebar h-full w-64 flex-shrink-0">
    <!-- Header -->
    <div class="border-b border-gray-200 p-4 dark:border-dark-border">
      <h1 class="text-lg font-semibold text-gray-900 dark:text-dark-text">
        ML Pipeline
      </h1>
    </div>

    <!-- New Run Button -->
    <div class="p-4">
      <button
        @click="$emit('new-run')"
        class="btn btn-primary w-full"
      >
        <span class="text-xl mr-2">+</span> New Run
      </button>
    </div>

    <!-- Search/Filter -->
    <div class="px-4 pb-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search runs..."
        class="input input-sm w-full"
      />
    </div>

    <!-- Run History -->
    <div class="flex-1 overflow-y-auto scrollbar-thin">
      <div v-if="loading" class="p-4">
        <div class="skeleton h-12 w-full rounded mb-2"></div>
        <div class="skeleton h-12 w-full rounded mb-2"></div>
        <div class="skeleton h-12 w-full rounded"></div>
      </div>

      <div v-else-if="filteredRuns.length === 0" class="p-4 text-center">
        <p class="text-sm text-gray-500 dark:text-dark-text-secondary">
          No runs found
        </p>
      </div>

      <div v-else>
        <!-- Today -->
        <div v-if="groupedRuns.today.length > 0" class="mb-4">
          <div class="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-dark-text-secondary">
            Today
          </div>
          <RunItem
            v-for="run in groupedRuns.today"
            :key="run.pipeline_run_id"
            :run="run"
            :active="selectedRunId === run.pipeline_run_id"
            @click="$emit('select-run', run)"
            @delete="$emit('delete-run', run.pipeline_run_id)"
            @stop="$emit('stop-run', run.pipeline_run_id)"
          />
        </div>

        <!-- Yesterday -->
        <div v-if="groupedRuns.yesterday.length > 0" class="mb-4">
          <div class="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-dark-text-secondary">
            Yesterday
          </div>
          <RunItem
            v-for="run in groupedRuns.yesterday"
            :key="run.pipeline_run_id"
            :run="run"
            :active="selectedRunId === run.pipeline_run_id"
            @click="$emit('select-run', run)"
            @delete="$emit('delete-run', run.pipeline_run_id)"
            @stop="$emit('stop-run', run.pipeline_run_id)"
          />
        </div>

        <!-- Last 7 Days -->
        <div v-if="groupedRuns.lastWeek.length > 0" class="mb-4">
          <div class="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-dark-text-secondary">
            Last 7 Days
          </div>
          <RunItem
            v-for="run in groupedRuns.lastWeek"
            :key="run.pipeline_run_id"
            :run="run"
            :active="selectedRunId === run.pipeline_run_id"
            @click="$emit('select-run', run)"
            @delete="$emit('delete-run', run.pipeline_run_id)"
            @stop="$emit('stop-run', run.pipeline_run_id)"
          />
        </div>

        <!-- Older -->
        <div v-if="groupedRuns.older.length > 0">
          <div class="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-dark-text-secondary">
            Older
          </div>
          <RunItem
            v-for="run in groupedRuns.older"
            :key="run.pipeline_run_id"
            :run="run"
            :active="selectedRunId === run.pipeline_run_id"
            @click="$emit('select-run', run)"
            @delete="$emit('delete-run', run.pipeline_run_id)"
            @stop="$emit('stop-run', run.pipeline_run_id)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import RunItem from '../history/RunItem.vue'

const props = defineProps({
  runs: {
    type: Array,
    default: () => []
  },
  selectedRunId: {
    type: String,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['new-run', 'select-run', 'delete-run', 'stop-run'])

const searchQuery = ref('')

const filteredRuns = computed(() => {
  if (!searchQuery.value) return props.runs

  const query = searchQuery.value.toLowerCase()
  return props.runs.filter(run =>
    run.pipeline_run_id?.toLowerCase().includes(query) ||
    run.experiment_name?.toLowerCase().includes(query)
  )
})

const groupedRuns = computed(() => {
  const groups = {
    today: [],
    yesterday: [],
    lastWeek: [],
    older: []
  }

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const lastWeek = new Date(today)
  lastWeek.setDate(lastWeek.getDate() - 7)

  filteredRuns.value.forEach(run => {
    const runDate = new Date(run.created_at || run.started_at)

    if (runDate >= today) {
      groups.today.push(run)
    } else if (runDate >= yesterday) {
      groups.yesterday.push(run)
    } else if (runDate >= lastWeek) {
      groups.lastWeek.push(run)
    } else {
      groups.older.push(run)
    }
  })

  return groups
})
</script>
