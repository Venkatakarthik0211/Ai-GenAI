import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: {
        title: 'ML Pipeline | Home'
      }
    },
    {
      // Catch-all 404 route
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/'
    }
  ]
})

// Update document title on route change
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'ML Pipeline'
  next()
})

export default router
