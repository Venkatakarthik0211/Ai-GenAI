import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/styles/main.css'

// Create Vue app instance
const app = createApp(App)

// Install Pinia store
const pinia = createPinia()
app.use(pinia)

// Install Vue Router
app.use(router)

// Mount app
app.mount('#app')
