import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // During Docker build, VITE_API_URL is set to "" so the app uses
  // relative URLs that nginx proxies to the backend container.
  // During local dev, it defaults to http://localhost:8000 (set in .env).
})
