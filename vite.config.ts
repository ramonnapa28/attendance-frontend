import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // This will proxy all /api requests to your FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // If your backend doesn't use /api as a prefix, set rewrite
        // rewrite: (path) => path.replace(/^\/api/, ''),
    },
    }
  }
})
