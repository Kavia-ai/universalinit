import { defineConfig } from 'vite'

export default defineConfig({
  server: {
      host: '0.0.0.0',
      allowedHosts: true,
      headers: {
          'Access-Control-Allow-Origin': '*'
      },
      watch: {
          usePolling: true
      }
  }
})
