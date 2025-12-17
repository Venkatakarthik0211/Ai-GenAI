<template>
  <div class="card w-full max-w-3xl mx-auto">
    <h2 class="mb-6 text-2xl font-bold">Create New Pipeline Run</h2>

    <!-- Natural Language Prompt -->
    <div class="mb-4">
      <label class="mb-2 block text-sm font-medium">
        Describe your ML task
        <span class="text-red-500">*</span>
      </label>
      <textarea
        v-model="formData.user_prompt"
        rows="4"
        class="input"
        :class="{ 'input-error': errors.user_prompt }"
        placeholder="Example: Classify iris species using random forest and SVM, optimize for accuracy"
      />
      <p v-if="errors.user_prompt" class="mt-1 text-xs text-red-600">
        {{ errors.user_prompt }}
      </p>
      <p class="mt-1 text-xs text-gray-500">
        Describe what you want to predict, which algorithms to use, and any specific requirements
      </p>
    </div>

    <!-- Data Path -->
    <div class="mb-4">
      <label class="mb-2 block text-sm font-medium">
        Data Path
        <span class="text-red-500">*</span>
      </label>
      <input
        v-model="formData.data_path"
        type="text"
        class="input"
        :class="{ 'input-error': errors.data_path }"
        placeholder="data/iris.csv"
      />
      <p v-if="errors.data_path" class="mt-1 text-xs text-red-600">
        {{ errors.data_path }}
      </p>
    </div>

    <!-- Experiment Name -->
    <div class="mb-4">
      <label class="mb-2 block text-sm font-medium">
        Experiment Name
      </label>
      <input
        v-model="formData.experiment_name"
        type="text"
        class="input"
        placeholder="ml_pipeline_experiment"
      />
      <p class="mt-1 text-xs text-gray-500">
        Leave blank to use default experiment name
      </p>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="mb-4 rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900 dark:text-red-200">
      <p class="font-medium">Error</p>
      <p class="text-sm">{{ error }}</p>
    </div>

    <!-- Actions -->
    <div class="flex gap-3">
      <button
        @click="handleSubmit"
        :disabled="loading || !isFormValid"
        class="btn btn-primary flex-1"
      >
        <span v-if="loading" class="flex items-center justify-center gap-2">
          <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-solid border-current border-r-transparent"></span>
          Starting Pipeline...
        </span>
        <span v-else>🚀 Start Pipeline</span>
      </button>
      <button
        v-if="onCancel"
        @click="onCancel"
        class="btn btn-secondary"
        :disabled="loading"
      >
        Cancel
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  onCancel: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['submit'])

const formData = ref({
  user_prompt: '',
  data_path: 'data/iris.csv',
  experiment_name: 'ml_pipeline_experiment'
})

const errors = ref({
  user_prompt: null,
  data_path: null
})

const isFormValid = computed(() => {
  return formData.value.user_prompt.trim() !== '' &&
         formData.value.data_path.trim() !== '' &&
         !errors.value.user_prompt &&
         !errors.value.data_path
})

watch(() => formData.value.user_prompt, (value) => {
  if (value.trim() === '') {
    errors.value.user_prompt = 'Please describe your ML task'
  } else {
    errors.value.user_prompt = null
  }
})

watch(() => formData.value.data_path, (value) => {
  if (value.trim() === '') {
    errors.value.data_path = 'Data path is required'
  } else {
    errors.value.data_path = null
  }
})

function handleSubmit() {
  // Validate
  if (!formData.value.user_prompt.trim()) {
    errors.value.user_prompt = 'Please describe your ML task'
    return
  }
  if (!formData.value.data_path.trim()) {
    errors.value.data_path = 'Data path is required'
    return
  }

  // Emit submit event
  emit('submit', { ...formData.value })
}

// Reset form
function reset() {
  formData.value = {
    user_prompt: '',
    data_path: 'data/iris.csv',
    experiment_name: 'ml_pipeline_experiment'
  }
  errors.value = {
    user_prompt: null,
    data_path: null
  }
}

// Expose reset method
defineExpose({ reset })
</script>
