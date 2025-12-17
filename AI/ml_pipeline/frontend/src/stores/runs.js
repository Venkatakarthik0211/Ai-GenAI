import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useRunsStore = defineStore('runs', () => {
  // State
  const runs = ref([])
  const selectedRun = ref(null)
  const filters = ref({
    status: null,
    experiment: null,
    dateRange: null
  })
  const loading = ref(false)

  // Getters
  const filteredRuns = computed(() => {
    let filtered = runs.value

    if (filters.value.status) {
      filtered = filtered.filter(run => run.status === filters.value.status)
    }

    if (filters.value.experiment) {
      filtered = filtered.filter(run =>
        run.experiment_name?.toLowerCase().includes(filters.value.experiment.toLowerCase())
      )
    }

    return filtered
  })

  const groupedByDate = computed(() => {
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
      const runDate = new Date(run.created_at)

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

  const runCount = computed(() => runs.value.length)

  // Actions
  function setRuns(newRuns) {
    runs.value = newRuns
  }

  function addRun(run) {
    // Add to beginning of array (most recent first)
    runs.value.unshift(run)
  }

  function updateRun(runId, updates) {
    const index = runs.value.findIndex(r => r.pipeline_run_id === runId)
    if (index !== -1) {
      runs.value[index] = { ...runs.value[index], ...updates }
    }
  }

  function removeRun(runId) {
    runs.value = runs.value.filter(r => r.pipeline_run_id !== runId)

    // Clear selectedRun if it was deleted
    if (selectedRun.value?.pipeline_run_id === runId) {
      selectedRun.value = null
    }
  }

  function selectRun(run) {
    selectedRun.value = run
  }

  function setFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function clearFilters() {
    filters.value = {
      status: null,
      experiment: null,
      dateRange: null
    }
  }

  function setLoading(isLoading) {
    loading.value = isLoading
  }

  return {
    // State
    runs,
    selectedRun,
    filters,
    loading,

    // Getters
    filteredRuns,
    groupedByDate,
    runCount,

    // Actions
    setRuns,
    addRun,
    updateRun,
    removeRun,
    selectRun,
    setFilters,
    clearFilters,
    setLoading
  }
})
