import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables from .env in the current directory
  const env = loadEnv(mode, process.cwd(), '')

  const port = parseInt(env.VITE_PORT || '3000', 10)
  const backendTarget = env.VITE_BACKEND_URL || 'http://localhost:3001'

  return {
    plugins: [
      react(),
      tailwindcss(),
    ],
    server: {
      port,
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
