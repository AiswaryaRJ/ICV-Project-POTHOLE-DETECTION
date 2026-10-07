import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy all /api requests to the FastAPI backend during dev
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Proxy static snapshots/proofs served by FastAPI
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Output the build to the backend's static/dist so FastAPI can serve it
    outDir: '../static/dist',
    emptyOutDir: true,
  },
})
