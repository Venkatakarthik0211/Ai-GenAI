<template>
  <div id="app" class="h-screen w-screen overflow-hidden bg-white dark:bg-dark-bg">
    <RouterView />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

// Check for dark mode preference on mount
onMounted(() => {
  // Check system preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.classList.add('dark')
  }

  // Check localStorage override
  const darkMode = localStorage.getItem('darkMode')
  if (darkMode === 'true') {
    document.documentElement.classList.add('dark')
  } else if (darkMode === 'false') {
    document.documentElement.classList.remove('dark')
  }
})
</script>

<style scoped>
/* App-level styles are in main.css */
</style>
