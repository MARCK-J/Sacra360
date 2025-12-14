import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy API requests to the API Gateway during development
    // The API gateway routes requests to the correct microservice (reports, documents, etc.).
    proxy: {
      '/api': {
        // During frontend development, proxy API calls directly to the Documents service
        // to avoid the placeholder API Gateway which doesn't forward routes.
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
